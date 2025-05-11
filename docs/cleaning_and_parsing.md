# Cleaning versus Parsing

By splitting them:
- Tests can target cleaning rules separately from parsing logic.
- You avoid tangled responsibilities (e.g., parsers trying to strip tags before extraction).
- You get clearer pipeline stages in your orchestrators

## Example:

```python
raw = downloader.download(...)
cleaned = cleaner.clean(raw)
parsed_docs, chunks = parser.parse(cleaned)
```

Cleaners: `cleaners\README.md`
Parsers: `parsers\README.md`
