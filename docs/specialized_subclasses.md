# Specialized Subclasses by Stage:

Do You Need Specialized Subclasses in Other Stages?
- Yes, sometimes — but only when the form type changes the logic or structure.

Let’s break this down by stage:

| Stage           | Specialization Required? | When?                                                                                                           |
| --------------- | ------------------------ | --------------------------------------------------------------------------------------------------------------- |
| **Downloaders** | **Rarely**               | Only if certain form types (e.g., Form 4 XML) require distinct URL logic or format handling.                    |
| **Cleaners**    | **Sometimes**            | If the HTML/XBRL structure varies significantly by form type.                                                   |
| **Parsers**     | **Frequently**           | Because each form (e.g., 10-K XBRL vs. Form 4 XML) has a different schema and logic.                            |
| **Writers**     | **Rarely**               | Only if the parsed result for a form type maps to a special DB structure (e.g., transactions table for Form 4). |
| **Embedders**   | **No**                   | All inputs should be normalized `ParsedChunk`s or `ParsedDocument`s before embedding.                           |
