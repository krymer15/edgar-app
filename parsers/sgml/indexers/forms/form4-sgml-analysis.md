# Form 4 SGML Structure Analysis

## Overview

This document analyzes the structure of Form 4 SGML/XML submissions in the SEC EDGAR system, specifically focused on the relationship between issuers and reporting owners. Form 4 filings report changes in beneficial ownership of securities and are submitted by insiders when they execute transactions in company securities.

## SGML Structure Components

Form 4 submissions contain several key structural components:

### 1. SEC Header Section

The `<SEC-HEADER>` section contains filing metadata including:
- Accession number
- Submission type
- Period of report
- Filed date
- Entity information (issuer and reporting owners)

### 2. Entity Information

Form 4 filings involve two primary entity types:

#### Issuer (Company)
Always a single entity marked by the `<ISSUER>` tag:
```
<ISSUER>		
    COMPANY DATA:	
        COMPANY CONFORMED NAME:    [Company Name]
        CENTRAL INDEX KEY:         [CIK Number]
        [Additional metadata...]
```

#### Reporting Owner(s)
Can be one or multiple entities, each marked by the `<REPORTING-OWNER>` tag:
```
<REPORTING-OWNER>	
    OWNER DATA:	
        COMPANY CONFORMED NAME:    [Owner Name]
        CENTRAL INDEX KEY:         [CIK Number]
        [Additional metadata...]
```

**Key Distinction**: SGML supports **1:N relationship** between issuer and reporting owners.

### 3. Document Section

Contains the actual Form 4 XML data:
```
<DOCUMENT>
<TYPE>4
<SEQUENCE>1
<FILENAME>[filename].xml
<DESCRIPTION>OWNERSHIP DOCUMENT
<TEXT>
<XML>
...
</XML>
</TEXT>
</DOCUMENT>
```

### 4. XML Content

Standardized XML structure containing:
- Schema information
- Issuer data
- Reporting owner data
- Transaction details
- Footnotes and remarks (if applicable)
- Owner signatures

## Entity Relationship Patterns

Based on the examined sample files, we identified two common patterns:

### Pattern 1: Single Reporting Owner (0001296720-25-000004.txt)
- One issuer (180 DEGREE CAPITAL CORP. /NY/ - CIK: 0000893739)
- One reporting owner (Wolfe Daniel B - CIK: 0001296720)
- Relationship: Officer and Director

### Pattern 2: Multiple Reporting Owners (0000921895-25-001190.txt)
- One issuer (1 800 FLOWERS COM INC - CIK: 0001084869)
- Multiple reporting owners:
  - Pleasant Lake Partners LLC (CIK: 0001580144)
  - PLP Funds Master Fund LP (CIK: 0002052009)
  - Fund 1 Investments, LLC (CIK: 0001959730)
- Relationship: 10% Owners operating as a group (explained in footnotes)

## SGML Extraction Points

For reliable processing, parsers must extract:

### 1. Issuer Information
- Location: `<ISSUER>` section → `CENTRAL INDEX KEY:`
- Always a single issuer per filing
- Required for URL construction and database association

### 2. Reporting Owner Information
- Location: Each `<REPORTING-OWNER>` section → `CENTRAL INDEX KEY:`
- May be one or multiple owners per filing
- Owner relationship information (director, officer, 10% owner)

### 3. Transaction Details
- Located in XML section under `<nonDerivativeTable>` or `<derivativeTable>`
- Contains transaction dates, share counts, prices, etc.

### 4. Supporting Information
- Footnotes explain relationships and ownership details
- Remarks provide additional context
- Signatures verify filing authenticity

## Recommended Parser Implementation

The parser should handle both single and multiple reporting owner scenarios:

```python
def extract_form4_entities(sgml_content: str) -> dict:
    """
    Extract issuer and all reporting owners from a Form 4 SGML filing.
    Handles both single and multiple reporting owner cases.
    """
    result = {
        "issuer": {
            "cik": None,
            "name": None
        },
        "reporting_owners": []
    }
    
    # Extract issuer information
    issuer_section_start = sgml_content.find("<ISSUER>")
    if issuer_section_start != -1:
        issuer_section_end = sgml_content.find("</ISSUER>", issuer_section_start)
        if issuer_section_end != -1:
            issuer_section = sgml_content[issuer_section_start:issuer_section_end]
            
            # Extract CIK
            cik_start = issuer_section.find("CENTRAL INDEX KEY:")
            if cik_start != -1:
                cik_line_end = issuer_section.find("\n", cik_start)
                cik_line = issuer_section[cik_start:cik_line_end]
                cik = ''.join(c for c in cik_line if c.isdigit())
                result["issuer"]["cik"] = cik
            
            # Extract name
            name_start = issuer_section.find("COMPANY CONFORMED NAME:")
            if name_start != -1:
                name_line_end = issuer_section.find("\n", name_start)
                name_line = issuer_section[name_start:name_line_end]
                parts = name_line.split(":")
                if len(parts) > 1:
                    result["issuer"]["name"] = parts[1].strip()
    
    # Extract all reporting owners (handles multiple owners)
    start_pos = 0
    while True:
        owner_start = sgml_content.find("<REPORTING-OWNER>", start_pos)
        if owner_start == -1:
            break
            
        owner_end = sgml_content.find("</REPORTING-OWNER>", owner_start)
        if owner_end == -1:
            break
            
        owner_section = sgml_content[owner_start:owner_end]
        owner_data = {}
        
        # Extract CIK
        cik_start = owner_section.find("CENTRAL INDEX KEY:")
        if cik_start != -1:
            cik_line_end = owner_section.find("\n", cik_start)
            cik_line = owner_section[cik_start:cik_line_end]
            owner_data["cik"] = ''.join(c for c in cik_line if c.isdigit())
        
        # Extract name
        name_start = owner_section.find("COMPANY CONFORMED NAME:")
        if name_start != -1:
            name_line_end = owner_section.find("\n", name_start)
            name_line = owner_section[name_start:name_line_end]
            parts = name_line.split(":")
            if len(parts) > 1:
                owner_data["name"] = parts[1].strip()
        
        if owner_data.get("cik"):
            result["reporting_owners"].append(owner_data)
        
        start_pos = owner_end + 1
    
    return result
```

## Edge Cases and Considerations

1. **Multiple Reporting Owners**
   - Group filings must associate all transactions with each listed owner
   - Relationships between owners often explained in footnotes

2. **Ownership Types**
   - Direct ownership (`D`) vs. Indirect ownership (`I`)
   - Nature of ownership may reference footnotes 

3. **Varied Transaction Types**
   - Non-derivative transactions (common stock)
   - Derivative transactions (options, warrants)
   - Multiple transactions in a single filing

4. **Relationship Types**
   - Director
   - Officer (with title)
   - 10% Owner
   - Other (with explanation)

5. **Historical Format Changes**
   - Older filings may have different tag structures
   - Variations in whitespace and formatting

## Implementation Recommendations

1. **Two-Phase Parsing**
   - First phase: Extract entity structure from SGML header
   - Second phase: Parse XML for detailed transaction data

2. **Robust Error Handling**
   - Handle missing tags or sections
   - Provide fallback extraction methods

3. **URL Construction**
   - Use issuer CIK for document retrieval 
   - Keep issuer/reporting owner association for relationships

4. **Database Schema**
   - Store many-to-many relationship between issuers and reporting owners
   - Normalize metadata to avoid duplication

## Future Tasks

### 1. Footnote Extraction

Footnotes contain critical information about ownership relationships and transaction context:

```xml
<footnotes>
    <footnote id="F1">Securities reported herein are held for the benefit of PLP Funds Master Fund LP...</footnote>
    <footnote id="F2">Securities held for the account of Master Fund.</footnote>
</footnotes>
```

**Implementation Tasks:**
- Create a footnote extraction function to map footnote IDs to content
- Parse footnote references in transaction data
- Add logic to interpret common footnote patterns

### 2. Transaction Detail Parsing

Transaction details are stored in structured XML:

```xml
<nonDerivativeTransaction>
    <securityTitle>
        <value>Common Stock</value>
    </securityTitle>
    <transactionDate>
        <value>2025-05-08</value>
    </transactionDate>
    <transactionCoding>
        <transactionFormType>4</transactionFormType>
        <transactionCode>P</transactionCode>
        <equitySwapInvolved>0</equitySwapInvolved>
    </transactionCoding>
    ...
</nonDerivativeTransaction>
```

**Implementation Tasks:**
- Develop parsers for both non-derivative and derivative transactions
- Extract transaction types, codes, and meanings
- Calculate transaction values and ownership changes
- Track cumulative ownership positions

### 3. Relationship Analysis

Form 4 filings contain valuable relationship information:

```xml
<reportingOwnerRelationship>
    <isDirector>1</isDirector>
    <isOfficer>1</isOfficer>
    <isTenPercentOwner>0</isTenPercentOwner>
    <isOther>0</isOther>
    <officerTitle>President</officerTitle>
</reportingOwnerRelationship>
```

**Implementation Tasks:**
- Extract and categorize relationship types
- Track changes in relationship status over time
- Build network graphs of issuers and reporting owners

### 4. Historical Trends

Transaction data can be analyzed for patterns:

**Implementation Tasks:**
- Implement time-series analysis of transaction behavior
- Create algorithms to detect unusual transaction patterns
- Build dashboards to visualize insider trading activity

## Testing Approach

1. **Test Fixtures**
   - Create fixtures for both single and multiple reporting owner scenarios
   - Include examples with footnotes and complex ownership

2. **Edge Case Testing**
   - Test with unusual formatting or whitespace
   - Test with missing sections or tags

3. **Integration Testing**
   - Verify correct URL construction with extracted CIKs
   - Validate database associations between entities

## Conclusion

Form 4 SGML/XML structure presents a manageable parsing challenge with careful attention to the 1:N relationship between issuers and reporting owners. The recommended approach separates entity extraction from transaction detail parsing to ensure robust handling of all possible Form 4 structures.
