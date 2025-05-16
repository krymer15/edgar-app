# SEC Filing SGML Structure Analysis

## Overview

SEC EDGAR submissions are stored as SGML (Standard Generalized Markup Language) text files that contain structured data about filings and the entities involved. This document outlines the SGML structure for different form types, focusing on how to extract essential entity information like issuer and reporting party CIKs.

## SGML Analysis Requirements

### Collection Requirements

1. **Representative Samples**:
   - Gather multiple `.txt` submission files for each form type
   - Include examples from different years (format may change over time)
   - Include examples with multiple reporting owners
   - Include examples with unusual characteristics (e.g., foreign entities)

2. **Key Form Types to Analyze**:
   - Ownership forms: 3, 4, 5
   - Beneficial ownership: 13D, 13G, 13F-HR
   - Restricted securities: 144
   - Tender offers: SC TO-I, SC TO-T
   - Business combinations: DEFM14A, 425, S-4

3. **Analysis Process**:
   - Document the main sections for each form type
   - Map the relationship between entities in each form
   - Identify consistent patterns for entity extraction
   - Create parsing rules for each form type

## SGML Structure By Form Type

### Common SEC Header Structure

All SGML submissions begin with a `<SEC-HEADER>` section containing metadata:

```html
<SEC-HEADER>0000320193-22-000001.hdr.sgml : 20220101
<ACCEPTANCE-DATETIME>20220101080000
ACCESSION NUMBER:		0000320193-22-000001
CONFORMED SUBMISSION TYPE:	4
PUBLIC DOCUMENT COUNT:		1
CONFORMED PERIOD OF REPORT:	20211231
FILED AS OF DATE:		20220101
DATE AS OF CHANGE:		20220101
```

This provides basic filing information but not the complete entity relationships.

### Form 3/4/5 Structure

Forms 3, 4, and 5 follow a consistent pattern with two primary sections:

```html
<ISSUER>
	COMPANY DATA:	
		COMPANY CONFORMED NAME:		APPLE INC
		CENTRAL INDEX KEY:		0000320193
		STANDARD INDUSTRIAL CLASSIFICATION:	[...]
		IRS NUMBER:			942404110
		STATE OF INCORPORATION:		CA
		FISCAL YEAR END:		0930
	BUSINESS ADDRESS:	
		STREET 1:		ONE APPLE PARK WAY
		CITY:			CUPERTINO
		STATE:			CA
		ZIP:			95014
		BUSINESS PHONE:		4089961010
</ISSUER>
<REPORTING-OWNER>
	OWNER DATA:	
		COMPANY CONFORMED NAME:		COOK TIMOTHY D
		CENTRAL INDEX KEY:		0001214156
	FILING VALUES:
		FORM TYPE:		4
		SEC ACT:		1934 Act
		SEC FILE NUMBER:	001-36743
		FILM NUMBER:		22500001
	MAIL ADDRESS:	
		STREET 1:		ONE APPLE PARK WAY
		STREET 2:		MS: 927-4GC
		CITY:			CUPERTINO
		STATE:			CA
		ZIP:			95014
</REPORTING-OWNER>
```

#### Key extraction points:

- Issuer CIK: Under <ISSUER> > CENTRAL INDEX KEY:
- Reporting Owner CIK: Under <REPORTING-OWNER> > CENTRAL INDEX KEY:
- Multiple reporting owners may have separate <REPORTING-OWNER> sections

### Form 13D/G Structure
Forms 13D and 13G use different terminology but follow a similar pattern:

```html
<SUBJECT-COMPANY>
	COMPANY DATA:	
		COMPANY CONFORMED NAME:		TWITTER INC
		CENTRAL INDEX KEY:		0001418091
		STANDARD INDUSTRIAL CLASSIFICATION:	[...]
		IRS NUMBER:			113786449
		STATE OF INCORPORATION:		DE
		FISCAL YEAR END:		1231
	BUSINESS ADDRESS:	
		STREET 1:		1355 MARKET STREET
		STREET 2:		SUITE 900
		CITY:			SAN FRANCISCO
		STATE:			CA
		ZIP:			94103
		BUSINESS PHONE:		4152229670
</SUBJECT-COMPANY>

<REPORTING-OWNER>
	OWNER DATA:	
		COMPANY CONFORMED NAME:		Musk Elon
		CENTRAL INDEX KEY:		0001494730
	FILING VALUES:
		FORM TYPE:		SC 13D
		SEC ACT:		1934 Act
		SEC FILE NUMBER:	005-90608
		FILM NUMBER:		22821164
	MAIL ADDRESS:	
		STREET 1:		2110 RANCH ROAD
		STREET 2:		620 SUITE B
		CITY:			AUSTIN
		STATE:			TX
		ZIP:			78734
</REPORTING-OWNER>
```
#### Key extraction points:

Subject Company (Issuer) CIK: Under <SUBJECT-COMPANY> > CENTRAL INDEX KEY:
Reporting Owner CIK: Under <REPORTING-OWNER> > CENTRAL INDEX KEY:

### Form 13F-HR Structure
Form 13F-HR is used by institutional investment managers:

```html
<REPORTING-OWNER>
	OWNER DATA:	
		COMPANY CONFORMED NAME:		BERKSHIRE HATHAWAY INC
		CENTRAL INDEX KEY:		0001067983
	FILING VALUES:
		FORM TYPE:		13F-HR
		SEC ACT:		1934 Act
		SEC FILE NUMBER:	028-05916
		FILM NUMBER:		22688744
	BUSINESS ADDRESS:	
		STREET 1:		3555 FARNAM STREET
		CITY:			OMAHA
		STATE:			NE
		ZIP:			68131
		BUSINESS PHONE:		4023461400
	MAIL ADDRESS:	
		STREET 1:		3555 FARNAM STREET
		CITY:			OMAHA
		STATE:			NE
		ZIP:			68131
</REPORTING-OWNER>
```

#### Key extraction points:

- Only has <REPORTING-OWNER> section (investment manager)
- Holdings are typically in a table or <informationTable> section

### Tender Offer (SC TO-I/T) Structure
Tender offers include different sections for the target and bidder:

```html
<SUBJECT-COMPANY>
	COMPANY DATA:	
		COMPANY CONFORMED NAME:		TARGET CORP
		CENTRAL INDEX KEY:		0000027419
		STANDARD INDUSTRIAL CLASSIFICATION:	RETAIL STORES [5331]
		IRS NUMBER:			410215170
		STATE OF INCORPORATION:		MN
		FISCAL YEAR END:		0131
	BUSINESS ADDRESS:	
		STREET 1:		1000 NICOLLET MALL
		CITY:			MINNEAPOLIS
		STATE:			MN
		ZIP:			55403
		BUSINESS PHONE:		6123046073
</SUBJECT-COMPANY>

<FILED-BY>
	COMPANY DATA:	
		COMPANY CONFORMED NAME:		BIDDER CORP
		CENTRAL INDEX KEY:		0000832988
		STANDARD INDUSTRIAL CLASSIFICATION:	SERVICES-ADVERTISING AGENCIES [7311]
		IRS NUMBER:			133519438
		STATE OF INCORPORATION:		DE
		FISCAL YEAR END:		1231
	BUSINESS ADDRESS:	
		STREET 1:		200 FIFTH AVENUE
		CITY:			NEW YORK
		STATE:			NY
		ZIP:			10010
		BUSINESS PHONE:		2125466000
</FILED-BY>
```

#### Key extraction points:

- Subject Company (Target) CIK: Under <SUBJECT-COMPANY> > CENTRAL INDEX KEY:
- Filed By (Bidder) CIK: Under <FILED-BY> > CENTRAL INDEX KEY:

### Form S-4/425/DEFM14A Structure (Business Combinations)
These forms often have more complex structures with multiple entities:

```html
<FILER>
	<COMPANY-DATA>
		<CONFORMED-NAME>ACQUIRING COMPANY INC</CONFORMED-NAME>
		<CIK>0000123456</CIK>
		<ASSIGNED-SIC>7374</ASSIGNED-SIC>
		<IRS-NUMBER>123456789</IRS-NUMBER>
		<STATE-OF-INCORPORATION>DE</STATE-OF-INCORPORATION>
		<FISCAL-YEAR-END>1231</FISCAL-YEAR-END>
	</COMPANY-DATA>
</FILER>

<TARGET-COMPANY>
	<COMPANY-DATA>
		<CONFORMED-NAME>TARGET COMPANY INC</CONFORMED-NAME>
		<CIK>0000654321</CIK>
		<ASSIGNED-SIC>7370</ASSIGNED-SIC>
		<IRS-NUMBER>987654321</IRS-NUMBER>
		<STATE-OF-INCORPORATION>CA</STATE-OF-INCORPORATION>
		<FISCAL-YEAR-END>1231</FISCAL-YEAR-END>
	</COMPANY-DATA>
</TARGET-COMPANY>
```

#### Key extraction points:

- Format may vary significantly between filings
- May include multiple companies with different roles
- Requires more sophisticated parsing logic

## Extraction Strategy
### General Extraction Approach

1. Section Identification:
- First locate the relevant sections using start/end tags
- Handle edge cases where closing tags might be missing

2. Line Parsing:
- Extract the CIK line using CENTRAL INDEX KEY: pattern
- Clean and normalize the extracted CIK (removing spaces, leading zeros)

3. Format Handling:
- Handle older formats (pre-2008) which may use different tag structures
- Account for variations in whitespace and formatting

### SGML Utility Functions
Example pattern for extracting issuer CIK:
```python
def extract_issuer_cik_from_sgml(sgml_content: str) -> str:
    """
    Extract the issuer CIK from SGML content.
    Works for Form 4/3/5 and similar forms.
    
    Args:
        sgml_content: Raw SGML content
        
    Returns:
        str: The issuer CIK or empty string if not found
    """
    # Try ISSUER section first (Forms 3/4/5)
    issuer_section_start = sgml_content.find("<ISSUER>")
    if issuer_section_start != -1:
        issuer_section_end = sgml_content.find("</ISSUER>", issuer_section_start)
        if issuer_section_end == -1:
            issuer_section_end = sgml_content.find("<REPORTING-OWNER>", issuer_section_start)
        
        if issuer_section_end != -1:
            issuer_section = sgml_content[issuer_section_start:issuer_section_end]
            
            cik_start = issuer_section.find("CENTRAL INDEX KEY:")
            if cik_start != -1:
                cik_line_end = issuer_section.find("\n", cik_start)
                if cik_line_end != -1:
                    cik_line = issuer_section[cik_start:cik_line_end]
                    cik = ''.join(c for c in cik_line if c.isdigit())
                    return cik
    
    # Try SUBJECT-COMPANY section next (Forms 13D/G, TO)
    subject_section_start = sgml_content.find("<SUBJECT-COMPANY>")
    if subject_section_start != -1:
        # Similar parsing logic...
    
    # Try additional formats as needed
    
    return ""
```
Expanded version should include all form types and handle edge cases.

### Form-Specific Extraction Examples

#### Form 4 Extraction
```python
# Form 4 example (specific parsing logic)
def extract_form4_entities(sgml_content: str) -> dict:
    """Extract all entities from a Form 4 filing."""
    result = {
        "issuer_cik": "",
        "reporting_owners": []
    }
    
    # Extract issuer
    issuer_cik = extract_issuer_cik_from_sgml(sgml_content)
    if issuer_cik:
        result["issuer_cik"] = issuer_cik
    
    # Extract all reporting owners
    owner_sections = []
    start_pos = 0
    while True:
        owner_start = sgml_content.find("<REPORTING-OWNER>", start_pos)
        if owner_start == -1:
            break
        
        owner_end = sgml_content.find("</REPORTING-OWNER>", owner_start)
        if owner_end == -1:
            break
        
        owner_sections.append(sgml_content[owner_start:owner_end])
        start_pos = owner_end
    
    # Process each owner section
    for section in owner_sections:
        cik_start = section.find("OWNER CIK:")
        if cik_start != -1:
            cik_line_end = section.find("\n", cik_start)
            if cik_line_end != -1:
                cik_line = section[cik_start:cik_line_end]
                owner_cik = ''.join(c for c in cik_line if c.isdigit())
                if owner_cik:
                    result["reporting_owners"].append(owner_cik)
    
    return result
```
## Recommendations for Implementation

1. Create Dedicated Parser Classes:
- Build form-specific parser classes that inherit from a base SGML parser
- Each class implements specialized extraction logic for its form type

2. Tiered Extraction Approach:
- Use a general extraction function first for common patterns
- Fall back to form-specific extractors for complex cases

3. Regular Testing:
- Create test fixtures with examples of each form type
- Ensure extractors work with real-world variations
- Update parsers when SEC changes formats

4. Error Handling:
- Implement robust error handling for mismatched tags
- Fall back to simpler extraction methods when detailed parsing fails
- Log parsing issues for future enhancement

## Next Steps
1. Collect representative SGML samples for each form type
2. Implement base extraction utilities for common patterns
3. Create form-specific extractors for complex form types
4. Develop comprehensive test suite with real-world examples
5. Integrate extraction logic with collector components

This markdown file provides a detailed technical reference for understanding and parsing the SGML structure of various SEC filings. It includes examples of different form types, extraction strategies, and recommendations for implementation. 

## Form Types with Special CIK Relationships

| Form Type | Relationship Type | Primary Sections | Description |
|-----------|------------------|------------------|-------------|
| Form 3    | Issuer/Reporting Owner | `<ISSUER>`, `<REPORTING-OWNER>` | Initial beneficial ownership |
| Form 4    | Issuer/Reporting Owner | `<ISSUER>`, `<REPORTING-OWNER>` | Changes in beneficial ownership |
| Form 5    | Issuer/Reporting Owner | `<ISSUER>`, `<REPORTING-OWNER>` | Annual beneficial ownership |
| 13D       | Issuer/Reporting Owner | `<SUBJECT-COMPANY>`, `<REPORTING-OWNER>` | Active ownership report |
| 13G       | Issuer/Reporting Owner | `<SUBJECT-COMPANY>`, `<REPORTING-OWNER>` | Passive ownership report |
| 13F-HR    | Institutional Investor/Holdings | `<REPORTING-OWNER>`, `<tableStart>` | Institutional holdings |
| 144       | Issuer/Seller | `<ISSUER>`, `<REPORTING-OWNER>` | Sale of restricted securities |
| SC TO-I   | Bidder/Target | `<SUBJECT-COMPANY>`, `<FILED-BY>` | Issuer tender offer |
| SC TO-T   | Bidder/Target | `<SUBJECT-COMPANY>`, `<FILED-BY>` | Third-party tender offer |
| DEFM14A   | Multiple Companies | Various | Merger proxy statement |
| 425       | Multiple Companies | Various | Business combination communications |
| S-4       | Multiple Companies | Various | Business combination registration |