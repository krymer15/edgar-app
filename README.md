# Safe Harbor EDGAR AI App

This repository powers the Safe Harbor EDGAR AI platform, an in-house system for ingesting, parsing, vectorizing, and AI-summarizing SEC EDGAR filings. It’s built around modular pipelines and clear data models.

## High-Level Structure

- **models/**  
  – Data model definitions (dataclasses + ORM) and adapters  
- **collectors/**  
  – Daily & bulk index fetchers  
- **downloaders/**  
  – Raw document download implementations  
- **cleaners/**  
  – Logic to clean raw SGML, HTML, XBRL, and form-specific XML  
- **parsers/**  
  – Logic to parse SGML, HTML, XBRL, and form-specific XML  
- **extractors/**  
  – Financial metrics, non-GAAP reconciliations, risk factors, etc.  
- **writers/**  
  – Persistence layers for metadata, documents, parsed chunks, vectors  
- **orchestrators/**  
  – Connectors that sequence crawlers → downloaders → parsers → writers  
- **monitors/**  
  – Scheduled or event-driven triggers (e.g. Form 4 polling)  
- **summarizers/**  
  – LLM wrappers for narrative summaries and signals  

Info on SEC Forms: `docs\sec_forms.md`

