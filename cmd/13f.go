package cmd

import (
	"context"
	"encoding/json"
	"encoding/xml"
	"fmt"
	"io"
	"net/http"
	"os"
	"path"
	"sort"
	"strconv"
	"strings"
	"text/tabwriter"
	"time"
	"unicode"

	"github.com/spf13/cobra"
)

const (
	secSubmissionsHost  = "https://data.sec.gov/submissions"
	secArchiveHost      = "https://www.sec.gov/Archives/edgar/data"
	secTickerURL        = "https://www.sec.gov/files/company_tickers.json"
	defaultSECUserAgent = "bw-cli/0.1.0 (set SEC_USER_AGENT with your contact)"
)

var (
	thirteenFLimit     int
	thirteenFQuery     string
	thirteenFList      bool
	thirteenFDetail    bool
	thirteenFRaw       bool
	thirteenFUserAgent string
)

var thirteenFCmd = &cobra.Command{
	Use:   "13f <cik-or-ticker>",
	Short: "Print latest SEC 13F holdings for a filing manager",
	Long: `Fetch the latest Form 13F-HR or 13F-HR/A filing from SEC EDGAR and print
its holdings.

Input can be a filing manager CIK, such as 1067983, or a public-company ticker
that SEC can resolve to a CIK, such as BRK-B. Most hedge funds and investment
managers should be queried by CIK.

If you are not sure what to query, run "bw 13f --list" to see common examples.
Use --query to filter holdings or to filter the built-in examples list. Use
--detail to include cover page, signature, summary, SEC file timestamps, other
managers, and voting authority fields.`,
	Example: `  bw 13f --list
  bw 13f --list --query buffett
  bw 13f 1067983 --limit 10
  bw 13f BRK-B --query apple
  bw 13f 1067983 --detail
  bw 13f 1067983 --raw --detail --limit 20`,
	Args: func(cmd *cobra.Command, args []string) error {
		if thirteenFList {
			if len(args) > 0 {
				return fmt.Errorf("--list does not accept an input")
			}
			return nil
		}
		return cobra.ExactArgs(1)(cmd, args)
	},
	Run: func(cmd *cobra.Command, args []string) {
		if thirteenFList {
			print13FManagerList(thirteenFQuery)
			return
		}
		if thirteenFLimit <= 0 {
			fmt.Fprintln(os.Stderr, "limit must be greater than 0")
			os.Exit(1)
		}

		ctx, cancel := context.WithTimeout(cmd.Context(), 25*time.Second)
		defer cancel()

		ua := secUserAgent()
		report, err := fetchLatest13FReport(ctx, args[0], ua, thirteenFDetail)
		if err != nil {
			fmt.Fprintf(os.Stderr, "failed to fetch 13F holdings: %v\n", err)
			os.Exit(1)
		}
		print13FReport(report, thirteenFPrintOptions{
			Limit:  thirteenFLimit,
			Query:  thirteenFQuery,
			Detail: thirteenFDetail,
			Raw:    thirteenFRaw,
		})
	},
}

func init() {
	thirteenFCmd.Flags().IntVarP(&thirteenFLimit, "limit", "n", 15, "maximum rows to print")
	thirteenFCmd.Flags().StringVarP(&thirteenFQuery, "query", "q", "", "filter by issuer, class, CUSIP, or put/call")
	thirteenFCmd.Flags().BoolVar(&thirteenFDetail, "detail", false, "show cover page, signature, summary, SEC file timestamps, other managers, and voting fields")
	thirteenFCmd.Flags().BoolVar(&thirteenFList, "list", false, "show common 13F filing managers and example inputs")
	thirteenFCmd.Flags().BoolVar(&thirteenFRaw, "raw", false, "show raw filing rows instead of aggregated positions")
	thirteenFCmd.Flags().StringVar(&thirteenFUserAgent, "user-agent", "", "SEC User-Agent header; defaults to SEC_USER_AGENT")
	rootCmd.AddCommand(thirteenFCmd)
}

type common13FManager struct {
	Name   string
	CIK    string
	Ticker string
	Note   string
}

var common13FManagers = []common13FManager{
	{Name: "H&H International Investment, LLC", CIK: "1759760", Note: "Duan Yongping / 段永平"},
	{Name: "Himalaya Capital Management LLC", CIK: "1709323", Note: "Li Lu / 李录"},
	{Name: "HHLR ADVISORS, LTD.", CIK: "1762304", Note: "Hillhouse / 高瓴"},
	{Name: "Greenwoods Asset Management Hong Kong Ltd.", CIK: "1848138", Note: "Greenwoods / 景林"},
	{Name: "Yiheng Capital Management, L.P.", CIK: "1447228", Note: "Yiheng / 一恒资本"},
	{Name: "BERKSHIRE HATHAWAY INC", CIK: "1067983", Ticker: "BRK-B", Note: "Warren Buffett"},
	{Name: "Scion Asset Management, LLC", CIK: "1649339", Note: "Michael Burry"},
	{Name: "Pershing Square Capital Management, L.P.", CIK: "1336528", Note: "Bill Ackman"},
	{Name: "Bridgewater Associates, LP", CIK: "1350694", Note: "Ray Dalio"},
	{Name: "RENAISSANCE TECHNOLOGIES LLC", CIK: "1037389", Note: "Jim Simons"},
	{Name: "CITADEL ADVISORS LLC", CIK: "1423053", Note: "Ken Griffin"},
	{Name: "Appaloosa LP", CIK: "1656456", Note: "David Tepper"},
	{Name: "SOROS FUND MANAGEMENT LLC", CIK: "1029160", Note: "George Soros"},
	{Name: "ARK Investment Management LLC", CIK: "1697748", Note: "Cathie Wood"},
	{Name: "TIGER GLOBAL MANAGEMENT LLC", CIK: "1167483", Note: "Public tech / growth"},
}

type thirteenFPrintOptions struct {
	Limit  int
	Query  string
	Detail bool
	Raw    bool
}

type thirteenFReport struct {
	ManagerName         string
	CIK                 string
	CIKNumber           string
	Form                string
	Accession           string
	FilingDate          string
	ReportDate          string
	ArchiveURL          string
	PrimaryDocumentFile string
	InfoTableFile       string
	ArchiveFiles        []secArchiveItem
	Detail              *thirteenFSubmissionDetail
	Holdings            []thirteenFHolding
}

type secIdentifier struct {
	CIK       string
	CIKNumber string
	Display   string
}

type secSubmissions struct {
	CIK     string `json:"cik"`
	Name    string `json:"name"`
	Filings struct {
		Recent secRecentFilings `json:"recent"`
	} `json:"filings"`
}

type secRecentFilings struct {
	AccessionNumber []string `json:"accessionNumber"`
	FilingDate      []string `json:"filingDate"`
	ReportDate      []string `json:"reportDate"`
	Form            []string `json:"form"`
	PrimaryDocument []string `json:"primaryDocument"`
}

type secFiling struct {
	Accession       string
	FilingDate      string
	ReportDate      string
	Form            string
	PrimaryDocument string
}

type secArchiveIndex struct {
	Directory struct {
		Items []secArchiveItem `json:"item"`
	} `json:"directory"`
}

type secArchiveItem struct {
	Name         string `json:"name"`
	LastModified string `json:"last-modified"`
	Size         string `json:"size"`
}

type secTickerRecord struct {
	CIK    int    `json:"cik_str"`
	Ticker string `json:"ticker"`
	Title  string `json:"title"`
}

type thirteenFInformationTable struct {
	Holdings []thirteenFHolding `xml:"infoTable"`
}

type thirteenFHolding struct {
	NameOfIssuer         string              `xml:"nameOfIssuer"`
	TitleOfClass         string              `xml:"titleOfClass"`
	CUSIP                string              `xml:"cusip"`
	Value                string              `xml:"value"`
	SharesOrPrincipalAmt thirteenFShareValue `xml:"shrsOrPrnAmt"`
	PutCall              string              `xml:"putCall"`
	InvestmentDiscretion string              `xml:"investmentDiscretion"`
	OtherManager         string              `xml:"otherManager"`
	VotingAuthority      thirteenFVoting     `xml:"votingAuthority"`
}

type thirteenFShareValue struct {
	Shares string `xml:"sshPrnamt"`
	Type   string `xml:"sshPrnamtType"`
}

type thirteenFVoting struct {
	Sole   string `xml:"Sole"`
	Shared string `xml:"Shared"`
	None   string `xml:"None"`
}

type thirteenFPosition struct {
	Issuer               string
	Class                string
	CUSIP                string
	PutCall              string
	Type                 string
	InvestmentDiscretion string
	OtherManager         string
	Value                int64
	Shares               int64
	VotingSole           int64
	VotingShared         int64
	VotingNone           int64
	Rows                 int
}

type thirteenFSubmissionDetail struct {
	SchemaVersion string `xml:"schemaVersion"`
	HeaderData    struct {
		SubmissionType string `xml:"submissionType"`
		FilerInfo      struct {
			LiveTestFlag   string `xml:"liveTestFlag"`
			PeriodOfReport string `xml:"periodOfReport"`
		} `xml:"filerInfo"`
	} `xml:"headerData"`
	FormData struct {
		CoverPage      thirteenFCoverPage      `xml:"coverPage"`
		SignatureBlock thirteenFSignatureBlock `xml:"signatureBlock"`
		SummaryPage    thirteenFSummaryPage    `xml:"summaryPage"`
	} `xml:"formData"`
}

type thirteenFCoverPage struct {
	ReportCalendarOrQuarter   string                 `xml:"reportCalendarOrQuarter"`
	IsAmendment               string                 `xml:"isAmendment"`
	AmendmentNumber           string                 `xml:"amendmentNumber"`
	AmendmentType             string                 `xml:"amendmentType"`
	FilingManager             thirteenFFilingManager `xml:"filingManager"`
	ReportType                string                 `xml:"reportType"`
	Form13FFileNumber         string                 `xml:"form13FFileNumber"`
	CRDNumber                 string                 `xml:"crdNumber"`
	SECFileNumber             string                 `xml:"secFileNumber"`
	ProvideInfoForInstruction string                 `xml:"provideInfoForInstruction5"`
}

type thirteenFFilingManager struct {
	Name    string           `xml:"name"`
	Address thirteenFAddress `xml:"address"`
}

type thirteenFAddress struct {
	Street1        string `xml:"street1"`
	Street2        string `xml:"street2"`
	City           string `xml:"city"`
	StateOrCountry string `xml:"stateOrCountry"`
	ZipCode        string `xml:"zipCode"`
}

type thirteenFSignatureBlock struct {
	Name           string `xml:"name"`
	Title          string `xml:"title"`
	Phone          string `xml:"phone"`
	Signature      string `xml:"signature"`
	City           string `xml:"city"`
	StateOrCountry string `xml:"stateOrCountry"`
	SignatureDate  string `xml:"signatureDate"`
}

type thirteenFSummaryPage struct {
	OtherIncludedManagersCount string                     `xml:"otherIncludedManagersCount"`
	TableEntryTotal            string                     `xml:"tableEntryTotal"`
	TableValueTotal            string                     `xml:"tableValueTotal"`
	IsConfidentialOmitted      string                     `xml:"isConfidentialOmitted"`
	OtherManagersInfo          thirteenFOtherManagersInfo `xml:"otherManagers2Info"`
}

type thirteenFOtherManagersInfo struct {
	Managers []thirteenFOtherManagerEntry `xml:"otherManager2"`
}

type thirteenFOtherManagerEntry struct {
	SequenceNumber string `xml:"sequenceNumber"`
	OtherManager   struct {
		Form13FFileNumber string `xml:"form13FFileNumber"`
		Name              string `xml:"name"`
		CRDNumber         string `xml:"crdNumber"`
		SECFileNumber     string `xml:"secFileNumber"`
		CIK               string `xml:"cik"`
	} `xml:"otherManager"`
}

func secUserAgent() string {
	if strings.TrimSpace(thirteenFUserAgent) != "" {
		return strings.TrimSpace(thirteenFUserAgent)
	}
	if ua := strings.TrimSpace(os.Getenv("SEC_USER_AGENT")); ua != "" {
		return ua
	}
	return defaultSECUserAgent
}

func fetchLatest13FReport(ctx context.Context, input, userAgent string, includeDetail bool) (*thirteenFReport, error) {
	identifier, err := resolveSECIdentifier(ctx, input, userAgent)
	if err != nil {
		return nil, err
	}

	submissions, err := fetchSECSubmissions(ctx, identifier.CIK, userAgent)
	if err != nil {
		return nil, err
	}

	filing, err := latest13FFiling(submissions.Filings.Recent)
	if err != nil {
		return nil, fmt.Errorf("%s: %w", identifier.Display, err)
	}

	tableFile, archiveFiles, holdings, err := fetch13FInformationTable(ctx, identifier.CIKNumber, filing, userAgent)
	if err != nil {
		return nil, err
	}

	archiveURL := secArchiveBaseURL(identifier.CIKNumber, filing.Accession)
	primaryFile := path.Base(filing.PrimaryDocument)
	var detail *thirteenFSubmissionDetail
	if includeDetail {
		primaryFile, detail, err = fetch13FSubmissionDetail(ctx, archiveURL, archiveFiles, filing, userAgent)
		if err != nil {
			return nil, err
		}
	}

	name := strings.TrimSpace(submissions.Name)
	if name == "" {
		name = identifier.Display
	}
	return &thirteenFReport{
		ManagerName:         name,
		CIK:                 identifier.CIK,
		CIKNumber:           identifier.CIKNumber,
		Form:                filing.Form,
		Accession:           filing.Accession,
		FilingDate:          filing.FilingDate,
		ReportDate:          filing.ReportDate,
		ArchiveURL:          archiveURL,
		PrimaryDocumentFile: primaryFile,
		InfoTableFile:       tableFile,
		ArchiveFiles:        archiveFiles,
		Detail:              detail,
		Holdings:            holdings,
	}, nil
}

func resolveSECIdentifier(ctx context.Context, input, userAgent string) (secIdentifier, error) {
	if cik, cikNumber, ok := normalizeCIK(input); ok {
		return secIdentifier{CIK: cik, CIKNumber: cikNumber, Display: "CIK " + cikNumber}, nil
	}

	ticker := strings.ToUpper(strings.TrimSpace(input))
	if ticker == "" {
		return secIdentifier{}, fmt.Errorf("CIK or ticker is required")
	}

	body, err := secGet(ctx, secTickerURL, userAgent)
	if err != nil {
		return secIdentifier{}, fmt.Errorf("resolve ticker %s: %w", ticker, err)
	}
	var records map[string]secTickerRecord
	if err := json.Unmarshal(body, &records); err != nil {
		return secIdentifier{}, fmt.Errorf("decode SEC ticker list: %w", err)
	}
	for _, record := range records {
		if strings.EqualFold(record.Ticker, ticker) {
			cik, cikNumber, ok := normalizeCIK(strconv.Itoa(record.CIK))
			if !ok {
				return secIdentifier{}, fmt.Errorf("invalid CIK %d for ticker %s", record.CIK, ticker)
			}
			display := ticker
			if record.Title != "" {
				display += " (" + record.Title + ")"
			}
			return secIdentifier{CIK: cik, CIKNumber: cikNumber, Display: display}, nil
		}
	}
	return secIdentifier{}, fmt.Errorf("ticker %q not found in SEC ticker list; pass the filing manager CIK instead", ticker)
}

func normalizeCIK(input string) (string, string, bool) {
	s := strings.TrimSpace(strings.ToUpper(input))
	s = strings.TrimPrefix(s, "CIK")
	s = strings.TrimSpace(s)
	if s == "" {
		return "", "", false
	}
	for _, r := range s {
		if !unicode.IsDigit(r) {
			return "", "", false
		}
	}
	cikNumber := strings.TrimLeft(s, "0")
	if cikNumber == "" {
		cikNumber = "0"
	}
	if len(cikNumber) > 10 {
		return "", "", false
	}
	return strings.Repeat("0", 10-len(cikNumber)) + cikNumber, cikNumber, true
}

func fetchSECSubmissions(ctx context.Context, cik, userAgent string) (*secSubmissions, error) {
	body, err := secGet(ctx, fmt.Sprintf("%s/CIK%s.json", secSubmissionsHost, cik), userAgent)
	if err != nil {
		return nil, err
	}
	var submissions secSubmissions
	if err := json.Unmarshal(body, &submissions); err != nil {
		return nil, fmt.Errorf("decode SEC submissions: %w", err)
	}
	return &submissions, nil
}

func latest13FFiling(recent secRecentFilings) (*secFiling, error) {
	n := min(
		len(recent.AccessionNumber),
		len(recent.FilingDate),
		len(recent.ReportDate),
		len(recent.Form),
		len(recent.PrimaryDocument),
	)
	for i := 0; i < n; i++ {
		form := strings.ToUpper(strings.TrimSpace(recent.Form[i]))
		if form != "13F-HR" && form != "13F-HR/A" {
			continue
		}
		return &secFiling{
			Accession:       recent.AccessionNumber[i],
			FilingDate:      recent.FilingDate[i],
			ReportDate:      recent.ReportDate[i],
			Form:            form,
			PrimaryDocument: recent.PrimaryDocument[i],
		}, nil
	}
	return nil, fmt.Errorf("no recent 13F-HR filing found")
}

func fetch13FInformationTable(ctx context.Context, cikNumber string, filing *secFiling, userAgent string) (string, []secArchiveItem, []thirteenFHolding, error) {
	baseURL := secArchiveBaseURL(cikNumber, filing.Accession)
	index, err := fetchSECArchiveIndex(ctx, baseURL, userAgent)
	if err != nil {
		return "", nil, nil, err
	}

	for _, name := range infoTableCandidates(*index, filing.PrimaryDocument) {
		tableURL := baseURL + "/" + name
		body, err := secGet(ctx, tableURL, userAgent)
		if err != nil {
			continue
		}
		holdings, err := parse13FInformationTable(body)
		if err == nil && len(holdings) > 0 {
			return name, index.Directory.Items, holdings, nil
		}
	}
	return "", index.Directory.Items, nil, fmt.Errorf("no parseable 13F information table found for accession %s", filing.Accession)
}

func secArchiveBaseURL(cikNumber, accession string) string {
	accessionDir := strings.ReplaceAll(accession, "-", "")
	return fmt.Sprintf("%s/%s/%s", secArchiveHost, cikNumber, accessionDir)
}

func fetchSECArchiveIndex(ctx context.Context, baseURL, userAgent string) (*secArchiveIndex, error) {
	body, err := secGet(ctx, baseURL+"/index.json", userAgent)
	if err != nil {
		return nil, err
	}
	var index secArchiveIndex
	if err := json.Unmarshal(body, &index); err != nil {
		return nil, fmt.Errorf("decode SEC archive index: %w", err)
	}
	return &index, nil
}

func fetch13FSubmissionDetail(ctx context.Context, baseURL string, archiveFiles []secArchiveItem, filing *secFiling, userAgent string) (string, *thirteenFSubmissionDetail, error) {
	for _, name := range primaryDocumentCandidates(archiveFiles, filing.PrimaryDocument) {
		body, err := secGet(ctx, baseURL+"/"+name, userAgent)
		if err != nil {
			continue
		}
		detail, err := parse13FSubmissionDetail(body)
		if err == nil && detail != nil {
			return name, detail, nil
		}
	}
	return "", nil, fmt.Errorf("no parseable 13F primary document found for accession %s", filing.Accession)
}

func infoTableCandidates(index secArchiveIndex, primaryDocument string) []string {
	primaryName := strings.ToLower(path.Base(primaryDocument))
	type candidate struct {
		name string
		size int64
	}
	candidates := make([]candidate, 0, len(index.Directory.Items))
	for _, item := range index.Directory.Items {
		name := strings.TrimSpace(item.Name)
		lower := strings.ToLower(name)
		if name == "" || !strings.HasSuffix(lower, ".xml") {
			continue
		}
		if lower == primaryName || strings.Contains(lower, "primary") {
			continue
		}
		size, _ := strconv.ParseInt(strings.TrimSpace(item.Size), 10, 64)
		candidates = append(candidates, candidate{name: name, size: size})
	}
	sort.SliceStable(candidates, func(i, j int) bool {
		return candidates[i].size > candidates[j].size
	})

	names := make([]string, 0, len(candidates))
	for _, candidate := range candidates {
		names = append(names, candidate.name)
	}
	if len(names) > 0 {
		return names
	}

	for _, item := range index.Directory.Items {
		name := strings.TrimSpace(item.Name)
		if strings.HasSuffix(strings.ToLower(name), ".xml") {
			names = append(names, name)
		}
	}
	return names
}

func primaryDocumentCandidates(items []secArchiveItem, primaryDocument string) []string {
	seen := map[string]bool{}
	names := []string{}
	add := func(name string) {
		name = strings.TrimSpace(path.Base(name))
		if name == "" || seen[name] {
			return
		}
		seen[name] = true
		names = append(names, name)
	}

	add(primaryDocument)
	for _, item := range items {
		name := strings.TrimSpace(item.Name)
		lower := strings.ToLower(name)
		if strings.HasSuffix(lower, ".xml") && strings.Contains(lower, "primary") {
			add(name)
		}
	}
	for _, item := range items {
		name := strings.TrimSpace(item.Name)
		if strings.HasSuffix(strings.ToLower(name), ".xml") {
			add(name)
		}
	}
	return names
}

func parse13FInformationTable(body []byte) ([]thirteenFHolding, error) {
	var table thirteenFInformationTable
	if err := xml.Unmarshal(body, &table); err != nil {
		return nil, fmt.Errorf("decode 13F information table: %w", err)
	}
	return table.Holdings, nil
}

func parse13FSubmissionDetail(body []byte) (*thirteenFSubmissionDetail, error) {
	var detail thirteenFSubmissionDetail
	if err := xml.Unmarshal(body, &detail); err != nil {
		return nil, fmt.Errorf("decode 13F primary document: %w", err)
	}
	if detail.HeaderData.SubmissionType == "" && detail.FormData.CoverPage.ReportType == "" {
		return nil, fmt.Errorf("not a 13F primary document")
	}
	return &detail, nil
}

func secGet(ctx context.Context, url, userAgent string) ([]byte, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("accept", "application/json, application/xml, text/xml, text/plain, */*")
	req.Header.Set("user-agent", userAgent)

	client := &http.Client{Timeout: 20 * time.Second}
	res, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()

	if res.StatusCode == http.StatusNotFound {
		return nil, fmt.Errorf("SEC resource not found: %s", url)
	}
	if res.StatusCode == http.StatusTooManyRequests {
		return nil, fmt.Errorf("SEC rate limit reached; retry later or use a more specific SEC_USER_AGENT")
	}
	if res.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("SEC http status %d for %s", res.StatusCode, url)
	}
	return io.ReadAll(res.Body)
}

func aggregate13FHoldings(holdings []thirteenFHolding) []thirteenFPosition {
	positions := make(map[string]*thirteenFPosition)
	order := make([]string, 0, len(holdings))
	for _, holding := range holdings {
		position := thirteenFPosition{
			Issuer:               clean13FText(holding.NameOfIssuer),
			Class:                clean13FText(holding.TitleOfClass),
			CUSIP:                clean13FText(holding.CUSIP),
			PutCall:              clean13FText(holding.PutCall),
			Type:                 clean13FText(holding.SharesOrPrincipalAmt.Type),
			InvestmentDiscretion: clean13FText(holding.InvestmentDiscretion),
			OtherManager:         clean13FText(holding.OtherManager),
			Value:                parse13FInt(holding.Value),
			Shares:               parse13FInt(holding.SharesOrPrincipalAmt.Shares),
			VotingSole:           parse13FInt(holding.VotingAuthority.Sole),
			VotingShared:         parse13FInt(holding.VotingAuthority.Shared),
			VotingNone:           parse13FInt(holding.VotingAuthority.None),
			Rows:                 1,
		}
		key := strings.Join([]string{
			strings.ToUpper(position.Issuer),
			strings.ToUpper(position.Class),
			strings.ToUpper(position.CUSIP),
			strings.ToUpper(position.PutCall),
			strings.ToUpper(position.Type),
		}, "\x00")
		if existing, ok := positions[key]; ok {
			existing.Value += position.Value
			existing.Shares += position.Shares
			existing.VotingSole += position.VotingSole
			existing.VotingShared += position.VotingShared
			existing.VotingNone += position.VotingNone
			existing.InvestmentDiscretion = merge13FText(existing.InvestmentDiscretion, position.InvestmentDiscretion)
			existing.OtherManager = merge13FManagerRefs(existing.OtherManager, position.OtherManager)
			existing.Rows++
			continue
		}
		positions[key] = &position
		order = append(order, key)
	}

	result := make([]thirteenFPosition, 0, len(positions))
	for _, key := range order {
		result = append(result, *positions[key])
	}
	sort13FPositions(result)
	return result
}

func raw13FPositions(holdings []thirteenFHolding) []thirteenFPosition {
	positions := make([]thirteenFPosition, 0, len(holdings))
	for _, holding := range holdings {
		positions = append(positions, thirteenFPosition{
			Issuer:               clean13FText(holding.NameOfIssuer),
			Class:                clean13FText(holding.TitleOfClass),
			CUSIP:                clean13FText(holding.CUSIP),
			PutCall:              clean13FText(holding.PutCall),
			Type:                 clean13FText(holding.SharesOrPrincipalAmt.Type),
			InvestmentDiscretion: clean13FText(holding.InvestmentDiscretion),
			OtherManager:         clean13FText(holding.OtherManager),
			Value:                parse13FInt(holding.Value),
			Shares:               parse13FInt(holding.SharesOrPrincipalAmt.Shares),
			VotingSole:           parse13FInt(holding.VotingAuthority.Sole),
			VotingShared:         parse13FInt(holding.VotingAuthority.Shared),
			VotingNone:           parse13FInt(holding.VotingAuthority.None),
			Rows:                 1,
		})
	}
	sort13FPositions(positions)
	return positions
}

func sort13FPositions(positions []thirteenFPosition) {
	sort.SliceStable(positions, func(i, j int) bool {
		if positions[i].Value == positions[j].Value {
			return positions[i].Issuer < positions[j].Issuer
		}
		return positions[i].Value > positions[j].Value
	})
}

func print13FReport(report *thirteenFReport, opts thirteenFPrintOptions) {
	positions := aggregate13FHoldings(report.Holdings)
	mode := "aggregated"
	if opts.Raw {
		positions = raw13FPositions(report.Holdings)
		mode = "raw"
	}
	positions = filter13FPositions(positions, opts.Query)

	totalValue, totalRows := int64(0), 0
	for _, position := range positions {
		totalValue += position.Value
		totalRows += position.Rows
	}

	fmt.Println()
	fmt.Printf("  %s  %s\n", bold(report.ManagerName), dim("CIK "+report.CIKNumber))
	fmt.Printf("  %s  %s  filed %s  accession %s\n",
		dim(report.Form), dim("period "+emptyDash(report.ReportDate)), emptyDash(report.FilingDate), report.Accession)
	fmt.Printf("  %s  %d positions / %d filing rows  value %s  source %s\n",
		dim(mode), len(positions), totalRows, formatUSD(totalValue), report.InfoTableFile)
	if strings.TrimSpace(opts.Query) != "" {
		fmt.Printf("  %s  %q\n", dim("filter"), strings.TrimSpace(opts.Query))
	}
	if opts.Detail {
		print13FDetail(report)
	}

	if len(positions) == 0 {
		fmt.Println()
		fmt.Println("  no holdings matched")
		fmt.Println()
		return
	}

	limit := opts.Limit
	if limit > len(positions) {
		limit = len(positions)
	}

	fmt.Println()
	tw := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
	if opts.Raw {
		if opts.Detail {
			fmt.Fprintln(tw, "  #\tIssuer\tClass\tCUSIP\tPut/Call\tValue\tShares\tType\tDiscretion\tManager\tVote S/S/N")
		} else {
			fmt.Fprintln(tw, "  #\tIssuer\tClass\tCUSIP\tPut/Call\tValue\tShares\tType")
		}
		for i, position := range positions[:limit] {
			print13FPositionRow(tw, i+1, position, opts.Detail, false)
		}
	} else {
		if opts.Detail {
			fmt.Fprintln(tw, "  #\tIssuer\tClass\tCUSIP\tPut/Call\tValue\tShares\tType\tRows\tDiscretion\tManager\tVote S/S/N")
		} else {
			fmt.Fprintln(tw, "  #\tIssuer\tClass\tCUSIP\tPut/Call\tValue\tShares\tType\tRows")
		}
		for i, position := range positions[:limit] {
			print13FPositionRow(tw, i+1, position, opts.Detail, true)
		}
	}
	_ = tw.Flush()
	fmt.Println()
}

func print13FPositionRow(tw *tabwriter.Writer, index int, position thirteenFPosition, detail, showRows bool) {
	fields := []any{
		index,
		clip13F(position.Issuer, 34),
		clip13F(position.Class, 16),
		position.CUSIP,
		emptyDash(position.PutCall),
		formatUSD(position.Value),
		formatCommaInt(position.Shares),
		emptyDash(position.Type),
	}
	format := "  %d\t%s\t%s\t%s\t%s\t%s\t%s\t%s"
	if showRows {
		format += "\t%d"
		fields = append(fields, position.Rows)
	}
	if detail {
		format += "\t%s\t%s\t%s"
		fields = append(fields,
			emptyDash(position.InvestmentDiscretion),
			emptyDash(position.OtherManager),
			votingSummary(position),
		)
	}
	format += "\n"
	fmt.Fprintf(tw, format, fields...)
}

func print13FDetail(report *thirteenFReport) {
	fmt.Println()
	fmt.Println(dim("  Filing detail"))
	printKV("  Archive", report.ArchiveURL)
	printKV("  Primary XML", formatArchiveFile(report.ArchiveFiles, report.PrimaryDocumentFile))
	printKV("  Info table", formatArchiveFile(report.ArchiveFiles, report.InfoTableFile))
	if fullText := firstArchiveFileWithSuffix(report.ArchiveFiles, ".txt"); fullText != "" {
		printKV("  Full text", formatArchiveFile(report.ArchiveFiles, fullText))
	}

	if report.Detail == nil {
		return
	}

	detail := report.Detail
	cover := detail.FormData.CoverPage
	summary := detail.FormData.SummaryPage
	signature := detail.FormData.SignatureBlock

	printKV("  Schema", detail.SchemaVersion)
	printKV("  Live/Test", detail.HeaderData.FilerInfo.LiveTestFlag)
	printKV("  Period", firstNonEmpty(cover.ReportCalendarOrQuarter, detail.HeaderData.FilerInfo.PeriodOfReport))
	printKV("  Report type", cover.ReportType)
	printKV("  Amendment", formatAmendment(cover))
	printKV("  13F file no", cover.Form13FFileNumber)
	printKV("  CRD no", cover.CRDNumber)
	printKV("  SEC file no", cover.SECFileNumber)
	printKV("  Manager", cover.FilingManager.Name)
	printKV("  Address", format13FAddress(cover.FilingManager.Address))
	printKV("  Signature", formatSignature(signature))
	printKV("  Summary rows", summary.TableEntryTotal)
	printKV("  Summary value", formatUSD(parse13FInt(summary.TableValueTotal)))
	printKV("  Confidential", summary.IsConfidentialOmitted)
	printKV("  Other mgr count", summary.OtherIncludedManagersCount)

	if len(summary.OtherManagersInfo.Managers) == 0 {
		return
	}

	fmt.Println()
	fmt.Println(dim("  Other included managers"))
	tw := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
	fmt.Fprintln(tw, "  #\t13F file no\tName\tCRD\tSEC file\tCIK")
	for _, manager := range summary.OtherManagersInfo.Managers {
		fmt.Fprintf(tw, "  %s\t%s\t%s\t%s\t%s\t%s\n",
			emptyDash(manager.SequenceNumber),
			emptyDash(manager.OtherManager.Form13FFileNumber),
			emptyDash(manager.OtherManager.Name),
			emptyDash(manager.OtherManager.CRDNumber),
			emptyDash(manager.OtherManager.SECFileNumber),
			emptyDash(manager.OtherManager.CIK),
		)
	}
	_ = tw.Flush()
}

func print13FManagerList(query string) {
	managers := filterCommon13FManagers(common13FManagers, query)

	fmt.Println()
	fmt.Printf("  %s\n", bold("Common 13F filing managers"))
	if strings.TrimSpace(query) != "" {
		fmt.Printf("  %s  %q\n", dim("filter"), strings.TrimSpace(query))
	}
	fmt.Println()

	if len(managers) == 0 {
		fmt.Println("  no managers matched")
		fmt.Println()
		return
	}

	tw := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
	fmt.Fprintln(tw, "  Manager\tCIK\tTicker\tKnown for\tExample")
	for _, manager := range managers {
		input := manager.CIK
		if manager.Ticker != "" {
			input = manager.Ticker
		}
		fmt.Fprintf(tw, "  %s\t%s\t%s\t%s\tbw 13f %s\n",
			manager.Name,
			manager.CIK,
			emptyDash(manager.Ticker),
			manager.Note,
			input,
		)
	}
	_ = tw.Flush()
	fmt.Println()
	fmt.Println("  Tip: CIK is the most reliable input. Ticker works only when SEC maps it to a public-company CIK.")
	fmt.Println()
}

func filterCommon13FManagers(managers []common13FManager, query string) []common13FManager {
	q := strings.ToUpper(strings.TrimSpace(query))
	if q == "" {
		return managers
	}
	filtered := make([]common13FManager, 0, len(managers))
	for _, manager := range managers {
		haystack := strings.ToUpper(strings.Join([]string{
			manager.Name,
			manager.CIK,
			manager.Ticker,
			manager.Note,
		}, " "))
		if strings.Contains(haystack, q) {
			filtered = append(filtered, manager)
		}
	}
	return filtered
}

func filter13FPositions(positions []thirteenFPosition, query string) []thirteenFPosition {
	q := strings.ToUpper(strings.TrimSpace(query))
	if q == "" {
		return positions
	}
	filtered := make([]thirteenFPosition, 0, len(positions))
	for _, position := range positions {
		haystack := strings.ToUpper(strings.Join([]string{
			position.Issuer,
			position.Class,
			position.CUSIP,
			position.PutCall,
			position.Type,
			position.InvestmentDiscretion,
			position.OtherManager,
		}, " "))
		if strings.Contains(haystack, q) {
			filtered = append(filtered, position)
		}
	}
	return filtered
}

func votingSummary(position thirteenFPosition) string {
	return fmt.Sprintf("%s/%s/%s",
		formatCommaInt(position.VotingSole),
		formatCommaInt(position.VotingShared),
		formatCommaInt(position.VotingNone),
	)
}

func merge13FText(left, right string) string {
	left = clean13FText(left)
	right = clean13FText(right)
	switch {
	case left == "":
		return right
	case right == "":
		return left
	}
	parts := strings.Split(left, ", ")
	for _, part := range parts {
		if part == right {
			return left
		}
	}
	return left + ", " + right
}

func merge13FManagerRefs(left, right string) string {
	seen := map[string]bool{}
	out := []string{}
	add := func(value string) {
		for _, part := range strings.Split(value, ",") {
			part = clean13FText(part)
			if part == "" || seen[part] {
				continue
			}
			seen[part] = true
			out = append(out, part)
		}
	}
	add(left)
	add(right)
	return strings.Join(out, ",")
}

func formatArchiveFile(items []secArchiveItem, name string) string {
	item, ok := findArchiveFile(items, name)
	if !ok {
		return emptyDash(name)
	}
	parts := []string{item.Name}
	if strings.TrimSpace(item.Size) != "" {
		parts = append(parts, item.Size+" bytes")
	}
	if strings.TrimSpace(item.LastModified) != "" {
		parts = append(parts, "updated "+item.LastModified)
	}
	return strings.Join(parts, " · ")
}

func findArchiveFile(items []secArchiveItem, name string) (secArchiveItem, bool) {
	name = strings.TrimSpace(path.Base(name))
	for _, item := range items {
		if strings.EqualFold(strings.TrimSpace(item.Name), name) {
			return item, true
		}
	}
	return secArchiveItem{}, false
}

func firstArchiveFileWithSuffix(items []secArchiveItem, suffix string) string {
	for _, item := range items {
		if strings.HasSuffix(strings.ToLower(strings.TrimSpace(item.Name)), strings.ToLower(suffix)) {
			return item.Name
		}
	}
	return ""
}

func firstNonEmpty(values ...string) string {
	for _, value := range values {
		if strings.TrimSpace(value) != "" {
			return value
		}
	}
	return ""
}

func formatAmendment(cover thirteenFCoverPage) string {
	value := emptyDash(cover.IsAmendment)
	if strings.TrimSpace(cover.AmendmentNumber) != "" {
		value += " #" + strings.TrimSpace(cover.AmendmentNumber)
	}
	if strings.TrimSpace(cover.AmendmentType) != "" {
		value += " " + strings.TrimSpace(cover.AmendmentType)
	}
	return value
}

func format13FAddress(address thirteenFAddress) string {
	parts := []string{}
	for _, value := range []string{
		address.Street1,
		address.Street2,
		address.City,
		address.StateOrCountry,
		address.ZipCode,
	} {
		if strings.TrimSpace(value) != "" {
			parts = append(parts, strings.TrimSpace(value))
		}
	}
	return strings.Join(parts, ", ")
}

func formatSignature(signature thirteenFSignatureBlock) string {
	name := firstNonEmpty(signature.Signature, signature.Name)
	parts := []string{}
	if name != "" {
		parts = append(parts, name)
	}
	if strings.TrimSpace(signature.Title) != "" {
		parts = append(parts, signature.Title)
	}
	location := strings.Join(nonEmpty13F(signature.City, signature.StateOrCountry), ", ")
	if location != "" {
		parts = append(parts, location)
	}
	if strings.TrimSpace(signature.SignatureDate) != "" {
		parts = append(parts, signature.SignatureDate)
	}
	if strings.TrimSpace(signature.Phone) != "" {
		parts = append(parts, signature.Phone)
	}
	return strings.Join(parts, " · ")
}

func nonEmpty13F(values ...string) []string {
	out := []string{}
	for _, value := range values {
		if strings.TrimSpace(value) != "" {
			out = append(out, strings.TrimSpace(value))
		}
	}
	return out
}

func parse13FInt(s string) int64 {
	cleaned := strings.ReplaceAll(strings.TrimSpace(s), ",", "")
	if cleaned == "" {
		return 0
	}
	if strings.Contains(cleaned, ".") {
		v, _ := strconv.ParseFloat(cleaned, 64)
		return int64(v)
	}
	v, _ := strconv.ParseInt(cleaned, 10, 64)
	return v
}

func clean13FText(s string) string {
	return strings.Join(strings.Fields(s), " ")
}

func emptyDash(s string) string {
	if strings.TrimSpace(s) == "" {
		return "-"
	}
	return s
}

func clip13F(s string, max int) string {
	if len(s) <= max {
		return s
	}
	if max <= 1 {
		return s[:max]
	}
	return s[:max-1] + "."
}

func formatUSD(v int64) string {
	sign := ""
	if v < 0 {
		sign = "-"
		v = -v
	}
	return sign + "$" + formatCommaInt(v)
}

func formatCommaInt(v int64) string {
	sign := ""
	if v < 0 {
		sign = "-"
		v = -v
	}
	s := strconv.FormatInt(v, 10)
	if len(s) <= 3 {
		return sign + s
	}
	var b strings.Builder
	lead := len(s) % 3
	if lead == 0 {
		lead = 3
	}
	b.WriteString(s[:lead])
	for i := lead; i < len(s); i += 3 {
		b.WriteString(",")
		b.WriteString(s[i : i+3])
	}
	return sign + b.String()
}
