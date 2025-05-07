
# Overview
To safely delete records from a parent table 'daily_index_metadata' that have foreign key relationships with child tables (parsed_sgml_metadata, exhibit_metadata), you need to handle referential integrity constraints correctly. Here's how you can approach this:

Safe Deletion from daily_index_metadata
🧠 Assumptions:
daily_index_metadata.accession_number is the primary key or at least a unique identifier.

parsed_sgml_metadata.accession_number and exhibit_metadata.accession_number are foreign keys referencing daily_index_metadata.accession_number.

-----

## Option 1: Use ON DELETE CASCADE (Schema-level)
If you're okay with automatically deleting child records when a parent is deleted, ensure your foreign keys are defined like this:

```sql
FOREIGN KEY (accession_number) REFERENCES daily_index_metadata(accession_number) ON DELETE CASCADE
```

Then a simple delete works:
```sql
DELETE FROM daily_index_metadata WHERE form_type = '424B5';
```

✅ Pros: Simple
❌ Cons: Deletes are permanent and recursive — be careful.

-----

## Option 2: Manual Deletion in Dependency Order (Safe Default)
If you don’t have cascading deletes, delete in this order:

1. Delete from child tables first:
```sql
DELETE FROM exhibit_metadata
WHERE accession_number IN (
    SELECT accession_number FROM daily_index_metadata WHERE form_type = '424B5'
);

DELETE FROM parsed_sgml_metadata
WHERE accession_number IN (
    SELECT accession_number FROM daily_index_metadata WHERE form_type = '424B5'
);
```

2. Then delete from the parent:
```sql
DELETE FROM daily_index_metadata WHERE form_type = '424B5';
```
✅ Pros: Explicit and controlled
✅ Best for production use where data retention rules matter.

-----