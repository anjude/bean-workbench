package cmd

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/spf13/cobra"
)

const stockAnalysisAPIHost = "https://stockanalysis.com/api"

type stockQuote struct {
	Symbol            string  `json:"symbol"`
	Exchange          string  `json:"ex"`
	Price             float64 `json:"p"`
	Change            float64 `json:"c"`
	ChangePercent     float64 `json:"cp"`
	PreviousClose     float64 `json:"cl"`
	Open              float64 `json:"o"`
	High              float64 `json:"h"`
	Low               float64 `json:"l"`
	Volume            float64 `json:"v"`
	High52            float64 `json:"h52"`
	Low52             float64 `json:"l52"`
	MarketStatus      string  `json:"ms"`
	UpdatedAt         string  `json:"u"`
	ExtendedEnabled   bool    `json:"e"`
	ExtendedPrice     float64 `json:"ep"`
	ExtendedChange    float64 `json:"ec"`
	ExtendedChangePct float64 `json:"ecp"`
	ExtendedSession   string  `json:"es"`
	ExtendedUpdatedAt string  `json:"eu"`
}

type stockQuoteResp struct {
	Status int        `json:"status"`
	Data   stockQuote `json:"data"`
}

type stockOverviewInfo struct {
	Title string `json:"t"`
	Value string `json:"v"`
}

type stockOverview struct {
	MarketCap    string              `json:"marketCap"`
	Revenue      string              `json:"revenue"`
	NetIncome    string              `json:"netIncome"`
	SharesOut    string              `json:"sharesOut"`
	EPS          string              `json:"eps"`
	PERatio      string              `json:"peRatio"`
	ForwardPE    string              `json:"forwardPE"`
	Dividend     string              `json:"dividend"`
	Beta         string              `json:"beta"`
	Analysts     string              `json:"analysts"`
	Target       string              `json:"target"`
	EarningsDate string              `json:"earningsDate"`
	Description  string              `json:"description"`
	InfoTable    []stockOverviewInfo `json:"infoTable"`
}

type stockOverviewResp struct {
	Status int           `json:"status"`
	Data   stockOverview `json:"data"`
}

var stockVerbose bool

var stockCmd = &cobra.Command{
	Use:   "stock <ticker>",
	Short: "Print real-time quote and basic info of a stock",
	Long:  "Fetch real-time quote of a US stock from stockanalysis.com. Use -v for fundamentals, analysts and company profile. Example: bw stock AAPL -v",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		ticker := strings.ToUpper(strings.TrimSpace(args[0]))
		if ticker == "" {
			fmt.Fprintln(os.Stderr, "ticker is required")
			os.Exit(1)
		}

		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()

		var (
			wg       sync.WaitGroup
			quote    *stockQuote
			overview *stockOverview
			qErr     error
			oErr     error
		)

		wg.Add(1)
		go func() {
			defer wg.Done()
			quote, qErr = fetchStockQuote(ctx, ticker)
		}()
		if stockVerbose {
			wg.Add(1)
			go func() {
				defer wg.Done()
				overview, oErr = fetchStockOverview(ctx, ticker)
			}()
		}
		wg.Wait()

		if qErr != nil {
			fmt.Fprintf(os.Stderr, "failed to fetch quote for %s: %v\n", ticker, qErr)
			os.Exit(1)
		}

		printStock(ticker, quote, overview, oErr, stockVerbose)
	},
}

func init() {
	stockCmd.Flags().BoolVarP(&stockVerbose, "verbose", "v", false, "show fundamentals, analysts and company profile")
	rootCmd.AddCommand(stockCmd)
}

func fetchStockQuote(ctx context.Context, ticker string) (*stockQuote, error) {
	url := stockAnalysisAPIHost + "/quotes/s/" + strings.ToLower(ticker)
	body, err := stockAnalysisGet(ctx, url)
	if err != nil {
		return nil, err
	}
	resp := &stockQuoteResp{}
	if err := json.Unmarshal(body, resp); err != nil {
		return nil, fmt.Errorf("decode quote: %w", err)
	}
	if resp.Status != 200 {
		return nil, fmt.Errorf("quote api status %d", resp.Status)
	}
	return &resp.Data, nil
}

func fetchStockOverview(ctx context.Context, ticker string) (*stockOverview, error) {
	url := stockAnalysisAPIHost + "/symbol/s/" + strings.ToLower(ticker) + "/overview"
	body, err := stockAnalysisGet(ctx, url)
	if err != nil {
		return nil, err
	}
	resp := &stockOverviewResp{}
	if err := json.Unmarshal(body, resp); err != nil {
		return nil, fmt.Errorf("decode overview: %w", err)
	}
	if resp.Status != 200 {
		return nil, fmt.Errorf("overview api status %d", resp.Status)
	}
	return &resp.Data, nil
}

func stockAnalysisGet(ctx context.Context, url string) ([]byte, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("accept", "*/*")
	req.Header.Set("referer", "https://stockanalysis.com/")
	req.Header.Set("user-agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

	client := &http.Client{Timeout: 10 * time.Second}
	res, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()

	if res.StatusCode == http.StatusNotFound {
		return nil, fmt.Errorf("stock not found")
	}
	if res.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("http status %d", res.StatusCode)
	}
	return io.ReadAll(res.Body)
}

func printStock(ticker string, q *stockQuote, o *stockOverview, oErr error, verbose bool) {
	extendedActive := q.ExtendedEnabled && q.ExtendedPrice > 0
	extendedIsLatest := extendedActive && !strings.EqualFold(q.MarketStatus, "open")

	fmt.Println()
	fmt.Printf("  %s  %s  %s\n", bold(ticker), dim(q.Exchange), dim(marketStatusLabel(q.MarketStatus)))

	regLabel := "Last Close"
	if strings.EqualFold(q.MarketStatus, "open") {
		regLabel = "Live"
	}
	printPriceLine(regLabel, q.Price, q.Change, q.ChangePercent, q.UpdatedAt, !extendedIsLatest)

	if extendedActive {
		label := q.ExtendedSession
		if label == "" {
			label = "Extended"
		}
		printPriceLine(label, q.ExtendedPrice, q.ExtendedChange, q.ExtendedChangePct, q.ExtendedUpdatedAt, extendedIsLatest)
	}

	if !verbose {
		fmt.Println()
		fmt.Printf("  %s  Open $%.2f  Prev $%.2f  Day $%.2f-$%.2f  Vol %s\n",
			dim("·"), q.Open, q.PreviousClose, q.Low, q.High, humanVolume(q.Volume),
		)
		fmt.Println()
		return
	}

	fmt.Println()
	fmt.Println(dim("  Quote"))
	printKV("  Open", fmt.Sprintf("$%.2f", q.Open))
	printKV("  Prev Close", fmt.Sprintf("$%.2f", q.PreviousClose))
	printKV("  Day Range", fmt.Sprintf("$%.2f - $%.2f", q.Low, q.High))
	printKV("  52W Range", fmt.Sprintf("$%.2f - $%.2f", q.Low52, q.High52))
	printKV("  Volume", humanVolume(q.Volume))

	if o != nil {
		fmt.Println()
		fmt.Println(dim("  Fundamentals"))
		printKV("  Market Cap", o.MarketCap)
		printKV("  Revenue (TTM)", o.Revenue)
		printKV("  Net Income", o.NetIncome)
		printKV("  Shares Out", o.SharesOut)
		printKV("  EPS", o.EPS)
		printKV("  P/E", o.PERatio)
		printKV("  Fwd P/E", o.ForwardPE)
		printKV("  Beta", o.Beta)
		printKV("  Dividend", o.Dividend)
		printKV("  Ex-Dividend", valueFromInfoTable(o.InfoTable, "Ex-Dividend Date"))
		printKV("  Earnings", o.EarningsDate)

		fmt.Println()
		fmt.Println(dim("  Analysts"))
		printKV("  Rating", o.Analysts)
		printKV("  Target", o.Target)

		if len(o.InfoTable) > 0 {
			fmt.Println()
			fmt.Println(dim("  Profile"))
			for _, row := range o.InfoTable {
				switch row.Title {
				case "Industry", "Sector", "IPO Date", "Employees", "Website":
					printKV("  "+row.Title, row.Value)
				}
			}
		}

		if o.Description != "" {
			fmt.Println()
			fmt.Println(dim("  About"))
			fmt.Printf("  %s\n", wrap(o.Description, 88, "  "))
		}
	} else if oErr != nil {
		fmt.Println()
		fmt.Printf("  %s %v\n", dim("(overview unavailable:"), oErr)
	}
	fmt.Println()
}

func printPriceLine(label string, price, change, changePct float64, updatedAt string, latest bool) {
	arrow, color, reset := trendStyle(changePct)
	marker := dim("○")
	tag := ""
	priceStr := fmt.Sprintf("$%.2f", price)
	changeStr := fmt.Sprintf("%s%s$%.2f (%+.2f%%)%s", color, arrow, change, changePct, reset)

	if latest {
		marker = color + "●" + reset
		priceStr = bold(priceStr)
		tag = "  " + color + "← latest" + reset
	} else {
		priceStr = dim(priceStr)
		changeStr = dim(fmt.Sprintf("%s$%.2f (%+.2f%%)", arrow, change, changePct))
	}

	line := fmt.Sprintf("  %s %-12s %s  %s", marker, label, priceStr, changeStr)
	if updatedAt != "" {
		line += "  " + dim(updatedAt)
	}
	line += tag
	fmt.Println(line)
}

func printKV(k, v string) {
	if strings.TrimSpace(v) == "" {
		return
	}
	fmt.Printf("%-18s %s\n", k, v)
}

func valueFromInfoTable(rows []stockOverviewInfo, title string) string {
	for _, r := range rows {
		if r.Title == title {
			return r.Value
		}
	}
	return ""
}

func trendStyle(pct float64) (arrow, color, reset string) {
	switch {
	case pct > 0:
		return "▲ +", "\x1b[31m", "\x1b[0m"
	case pct < 0:
		return "▼ ", "\x1b[32m", "\x1b[0m"
	default:
		return "• ", "", ""
	}
}

func bold(s string) string { return "\x1b[1m" + s + "\x1b[0m" }
func dim(s string) string  { return "\x1b[2m" + s + "\x1b[0m" }

func marketStatusLabel(ms string) string {
	switch strings.ToLower(ms) {
	case "open":
		return "market open"
	case "closed":
		return "market closed"
	case "pre":
		return "pre-market"
	case "post":
		return "after-hours"
	default:
		return ms
	}
}

func humanVolume(v float64) string {
	switch {
	case v >= 1e9:
		return fmt.Sprintf("%.2fB", v/1e9)
	case v >= 1e6:
		return fmt.Sprintf("%.2fM", v/1e6)
	case v >= 1e3:
		return fmt.Sprintf("%.2fK", v/1e3)
	default:
		return fmt.Sprintf("%.0f", v)
	}
}

func wrap(s string, width int, indent string) string {
	words := strings.Fields(s)
	if len(words) == 0 {
		return s
	}
	var b strings.Builder
	line := words[0]
	for _, w := range words[1:] {
		if len(line)+1+len(w) > width {
			b.WriteString(line)
			b.WriteString("\n")
			b.WriteString(indent)
			line = w
		} else {
			line += " " + w
		}
	}
	b.WriteString(line)
	return b.String()
}
