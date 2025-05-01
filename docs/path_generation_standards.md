# /docs/path_generation_standards.md

## Test Mode vs Production Mode

By default, all saved file paths point to `/data/`.

To write to `/test_data/` instead, use the `--env test` flag in your CLI commands:

```bash
python scripts/ingest_from_source.py --source daily_index --date 2025-04-25 --env test
```

To work correctly:

The ConfigLoader override must be executed before any module uses the config.

This is implemented at the top of scripts/ingest_from_source.py.

The base_data_path in config/app_config.yaml will only be used if --env is not provided.

