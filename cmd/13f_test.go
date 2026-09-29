package cmd

import "testing"

func TestNormalizeCIK(t *testing.T) {
	tests := []struct {
		input     string
		wantCIK   string
		wantShort string
		wantOK    bool
	}{
		{input: "1067983", wantCIK: "0001067983", wantShort: "1067983", wantOK: true},
		{input: "CIK0001067983", wantCIK: "0001067983", wantShort: "1067983", wantOK: true},
		{input: "BRK-B", wantOK: false},
		{input: "12345678901", wantOK: false},
	}

	for _, tt := range tests {
		gotCIK, gotShort, gotOK := normalizeCIK(tt.input)
		if gotOK != tt.wantOK {
			t.Fatalf("normalizeCIK(%q) ok = %v, want %v", tt.input, gotOK, tt.wantOK)
		}
		if gotCIK != tt.wantCIK || gotShort != tt.wantShort {
			t.Fatalf("normalizeCIK(%q) = (%q, %q), want (%q, %q)", tt.input, gotCIK, gotShort, tt.wantCIK, tt.wantShort)
		}
	}
}

func TestParseAndAggregate13FInformationTable(t *testing.T) {
	xmlBody := []byte(`
<informationTable xmlns="http://www.sec.gov/edgar/document/thirteenf/informationtable">
  <infoTable>
    <nameOfIssuer>APPLE INC</nameOfIssuer>
    <titleOfClass>COM</titleOfClass>
    <cusip>037833100</cusip>
    <value>1000</value>
    <shrsOrPrnAmt>
      <sshPrnamt>10</sshPrnamt>
      <sshPrnamtType>SH</sshPrnamtType>
    </shrsOrPrnAmt>
    <investmentDiscretion>SOLE</investmentDiscretion>
    <votingAuthority>
      <Sole>10</Sole>
      <Shared>0</Shared>
      <None>0</None>
    </votingAuthority>
  </infoTable>
  <infoTable>
    <nameOfIssuer>APPLE   INC</nameOfIssuer>
    <titleOfClass>COM</titleOfClass>
    <cusip>037833100</cusip>
    <value>2500</value>
    <shrsOrPrnAmt>
      <sshPrnamt>25</sshPrnamt>
      <sshPrnamtType>SH</sshPrnamtType>
    </shrsOrPrnAmt>
    <investmentDiscretion>SOLE</investmentDiscretion>
    <otherManager>1,2</otherManager>
    <votingAuthority>
      <Sole>20</Sole>
      <Shared>3</Shared>
      <None>2</None>
    </votingAuthority>
  </infoTable>
  <infoTable>
    <nameOfIssuer>MICROSOFT CORP</nameOfIssuer>
    <titleOfClass>COM</titleOfClass>
    <cusip>594918104</cusip>
    <value>500</value>
    <shrsOrPrnAmt>
      <sshPrnamt>2</sshPrnamt>
      <sshPrnamtType>SH</sshPrnamtType>
    </shrsOrPrnAmt>
  </infoTable>
</informationTable>`)

	holdings, err := parse13FInformationTable(xmlBody)
	if err != nil {
		t.Fatalf("parse13FInformationTable() error = %v", err)
	}
	if len(holdings) != 3 {
		t.Fatalf("len(holdings) = %d, want 3", len(holdings))
	}

	positions := aggregate13FHoldings(holdings)
	if len(positions) != 2 {
		t.Fatalf("len(positions) = %d, want 2", len(positions))
	}
	if positions[0].Issuer != "APPLE INC" {
		t.Fatalf("positions[0].Issuer = %q, want APPLE INC", positions[0].Issuer)
	}
	if positions[0].Value != 3500 {
		t.Fatalf("positions[0].Value = %d, want 3500", positions[0].Value)
	}
	if positions[0].Shares != 35 {
		t.Fatalf("positions[0].Shares = %d, want 35", positions[0].Shares)
	}
	if positions[0].Rows != 2 {
		t.Fatalf("positions[0].Rows = %d, want 2", positions[0].Rows)
	}
	if positions[0].VotingSole != 30 || positions[0].VotingShared != 3 || positions[0].VotingNone != 2 {
		t.Fatalf("positions[0] voting = %d/%d/%d, want 30/3/2", positions[0].VotingSole, positions[0].VotingShared, positions[0].VotingNone)
	}
	if positions[0].InvestmentDiscretion != "SOLE" {
		t.Fatalf("positions[0].InvestmentDiscretion = %q, want SOLE", positions[0].InvestmentDiscretion)
	}
	if positions[0].OtherManager != "1,2" {
		t.Fatalf("positions[0].OtherManager = %q, want 1,2", positions[0].OtherManager)
	}
}

func TestInfoTableCandidates(t *testing.T) {
	index := secArchiveIndex{}
	index.Directory.Items = []secArchiveItem{
		{Name: "primary_doc.xml", Size: "5556"},
		{Name: "small.xml", Size: "100"},
		{Name: "large.xml", Size: "1000"},
		{Name: "filing.txt", Size: "2000"},
	}

	got := infoTableCandidates(index, "xslForm13F_X02/primary_doc.xml")
	want := []string{"large.xml", "small.xml"}
	if len(got) != len(want) {
		t.Fatalf("len(infoTableCandidates) = %d, want %d: %#v", len(got), len(want), got)
	}
	for i := range want {
		if got[i] != want[i] {
			t.Fatalf("infoTableCandidates[%d] = %q, want %q", i, got[i], want[i])
		}
	}
}

func TestParse13FSubmissionDetail(t *testing.T) {
	xmlBody := []byte(`
<edgarSubmission xmlns:ns1="http://www.sec.gov/edgar/common" xmlns="http://www.sec.gov/edgar/thirteenffiler">
  <schemaVersion>X0202</schemaVersion>
  <headerData>
    <submissionType>13F-HR</submissionType>
    <filerInfo>
      <liveTestFlag>LIVE</liveTestFlag>
      <periodOfReport>12-31-2025</periodOfReport>
    </filerInfo>
  </headerData>
  <formData>
    <coverPage>
      <reportCalendarOrQuarter>12-31-2025</reportCalendarOrQuarter>
      <isAmendment>false</isAmendment>
      <filingManager>
        <name>H&amp;H International Investment, LLC</name>
        <address>
          <ns1:street1>2479 E BAYSHORE RD #120</ns1:street1>
          <ns1:city>PALO ALTO</ns1:city>
          <ns1:stateOrCountry>CA</ns1:stateOrCountry>
          <ns1:zipCode>94303</ns1:zipCode>
        </address>
      </filingManager>
      <reportType>13F HOLDINGS REPORT</reportType>
      <form13FFileNumber>028-19454</form13FFileNumber>
    </coverPage>
    <signatureBlock>
      <name>Eric Hu</name>
      <title>Chief Compliance Officer</title>
      <phone>650-319-6832</phone>
      <signature>/s/Eric Hu</signature>
      <city>Palo Alto</city>
      <stateOrCountry>CA</stateOrCountry>
      <signatureDate>02-17-2026</signatureDate>
    </signatureBlock>
    <summaryPage>
      <otherIncludedManagersCount>1</otherIncludedManagersCount>
      <tableEntryTotal>14</tableEntryTotal>
      <tableValueTotal>17488569921</tableValueTotal>
      <isConfidentialOmitted>false</isConfidentialOmitted>
      <otherManagers2Info>
        <otherManager2>
          <sequenceNumber>1</sequenceNumber>
          <otherManager>
            <form13FFileNumber>28-2226</form13FFileNumber>
            <name>Example Manager</name>
          </otherManager>
        </otherManager2>
      </otherManagers2Info>
    </summaryPage>
  </formData>
</edgarSubmission>`)

	detail, err := parse13FSubmissionDetail(xmlBody)
	if err != nil {
		t.Fatalf("parse13FSubmissionDetail() error = %v", err)
	}
	if detail.SchemaVersion != "X0202" {
		t.Fatalf("SchemaVersion = %q, want X0202", detail.SchemaVersion)
	}
	if detail.FormData.CoverPage.FilingManager.Name != "H&H International Investment, LLC" {
		t.Fatalf("manager = %q", detail.FormData.CoverPage.FilingManager.Name)
	}
	if detail.FormData.CoverPage.FilingManager.Address.Street1 != "2479 E BAYSHORE RD #120" {
		t.Fatalf("street1 = %q", detail.FormData.CoverPage.FilingManager.Address.Street1)
	}
	if detail.FormData.SummaryPage.TableValueTotal != "17488569921" {
		t.Fatalf("TableValueTotal = %q", detail.FormData.SummaryPage.TableValueTotal)
	}
	if len(detail.FormData.SummaryPage.OtherManagersInfo.Managers) != 1 {
		t.Fatalf("other managers = %d, want 1", len(detail.FormData.SummaryPage.OtherManagersInfo.Managers))
	}
}

func TestFilterCommon13FManagers(t *testing.T) {
	got := filterCommon13FManagers(common13FManagers, "buffett")
	if len(got) != 1 {
		t.Fatalf("len(filterCommon13FManagers) = %d, want 1", len(got))
	}
	if got[0].CIK != "1067983" {
		t.Fatalf("matched CIK = %q, want 1067983", got[0].CIK)
	}

	got = filterCommon13FManagers(common13FManagers, "段永平")
	if len(got) != 1 {
		t.Fatalf("len(filterCommon13FManagers Chinese) = %d, want 1", len(got))
	}
	if got[0].CIK != "1759760" {
		t.Fatalf("matched Chinese CIK = %q, want 1759760", got[0].CIK)
	}

	got = filterCommon13FManagers(common13FManagers, "duan")
	if len(got) != 1 {
		t.Fatalf("len(filterCommon13FManagers pinyin) = %d, want 1", len(got))
	}
	if got[0].CIK != "1759760" {
		t.Fatalf("matched pinyin CIK = %q, want 1759760", got[0].CIK)
	}
}

func TestCommon13FManagersHaveValidCIKs(t *testing.T) {
	for _, manager := range common13FManagers {
		gotCIK, gotNumber, ok := normalizeCIK(manager.CIK)
		if !ok {
			t.Fatalf("%s has invalid CIK %q", manager.Name, manager.CIK)
		}
		if gotCIK == "" || gotNumber != manager.CIK {
			t.Fatalf("%s normalized CIK = (%q, %q), want number %q", manager.Name, gotCIK, gotNumber, manager.CIK)
		}
	}
}
