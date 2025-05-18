# SEC Forms

Resource links: https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data

---
## SEC Forms to include for analysis
Core Financial Reporting:
| **Form**        | **Purpose**                                     | **Data Format**        | **Why It Matters**                                                                 |
| --------------- | ----------------------------------------------- | ---------------------- | ---------------------------------------------------------------------------------- |
| **10-K**        | Annual financials + business risk               | XBRL, HTML             | Gold standard for long-term analysis: strategy, risk factors, full GAAP financials |
| **10-Q**        | Quarterly financials                            | XBRL, HTML             | Timely updates to earnings, margins, balance sheet                                 |
| **8-K**         | Current events (earnings, M\&A, CFO exit, etc.) | HTML, SGML             | Market-moving events, often parsed via Exhibit 99.1                                |
| **20-F / 40-F** | Non-US company annuals                          | HTML, XBRL (sometimes) | Equivalent to 10-Ks for foreign issuers                                            |
| **6-K**         | Foreign issuer interim updates                  | HTML                   | Similar to 8-Ks for international firms                                            |

Insider and Shareholder Activity:
| **Form**        | **Purpose**                      | **Data Format**           | **Why It Matters**                                   |
| --------------- | -------------------------------- | ------------------------- | ---------------------------------------------------- |
| **Form 4**      | Insider transactions             | XML                       | High-signal for conviction or exit behavior          |
| **Forms 3 / 5** | Insider ownership                | XML                       | Used for establishing patterns or delays             |
| **13D / 13G**   | Ownership >5%                    | HTML, SGML                | Track activist investors and hedge fund stakes       |
| **13F-HR**      | Quarterly institutional holdings | Text/XML (external feeds) | Portfolio tracking for funds, hedge fund replication |

Capital Markets & Offerings:
| **Form**      | **Purpose**                   | **Data Format** | **Why It Matters**                                   |
| ------------- | ----------------------------- | --------------- | ---------------------------------------------------- |
| **S-1 / F-1** | IPO filings                   | HTML            | Valuation, dilution, business model insights pre-IPO |
| **S-3 / F-3** | Follow-on offerings           | HTML            | Secondary offerings, shelf registrations             |
| **424B**      | Prospectus supplements        | HTML            | Final terms of IPOs or secondary offerings           |
| **S-4**       | M\&A transaction registration | HTML            | Merger financials and fairness opinions              |

Governance & Compensation:
| **Form**            | **Purpose**                | **Data Format** | **Why It Matters**                          |
| ------------------- | -------------------------- | --------------- | ------------------------------------------- |
| **DEF 14A (Proxy)** | Board elections, exec comp | HTML            | CEO comp, board independence, activism      |
| **SC TO-C / TO-I**  | Tender offers              | HTML            | Buyback, takeover, and arbitrage situations |
| **SD**              | Conflict minerals          | HTML            | Often low signal unless ESG-focused         |

Credit & Capital Structure (Optional)
| **Form**   | **Purpose**                         | **Data Format** | **Why It Matters**                         |
| ---------- | ----------------------------------- | --------------- | ------------------------------------------ |
| **10-D**   | Asset-backed security distributions | HTML            | Relevant for MBS/ABS or structured credit  |
| **ABS-EE** | XML for structured securities       | XML             | XBRL-style data for fixed income analytics |

XML-heavy forms:
| Form       | XML Use               | High Value for | Ingestion Priority |
| ---------- | --------------------- | -------------- | ------------------ |
| **4**      | Native XML            | Insider trades | ✅ High             |
| **3/5**    | Native XML            | Ownership      | ✅ Medium           |
| **10-K/Q** | XBRL/XML              | Fundamentals   | ✅ High             |
| **8-K**    | XML exhibits possible | Event tracking | ✅ Medium           |
| **13F**    | Occasionally in XML   | Fund positions | ⚠️ Optional        |

Top Forms for Deep Parsing:
| **Tier**              | **Form Types**                                             | **Data**        |
| --------------------- | ---------------------------------------------------------- | --------------- |
| 🥇 Core Must-Haves    | `10-K`, `10-Q`, `8-K`, `Form 4`, `S-1`, `13D/G`, `DEF 14A` | HTML, XBRL, XML |
| 🥈 Secondary Priority | `20-F`, `6-K`, `13F`, `424B`, `S-4`                        | HTML/XML        |
| 🥉 Niche/Optional     | `ABS-EE`, `10-D`, `SD`, `SC TO-C`                          | XML/HTML        |