---
name: certificate-reader
description: Read one document image or its OCR text into typed fields, each with a verbatim quote that code verifies.
---

# certificate-reader

## When to use
Read one document image or its OCR text into typed fields, each with a verbatim quote that code verifies.

## Inputs
OCR text of one document. Identifiers are replaced by placeholders before any model sees it.

## Outputs
Doc type, administration, capacity, issue and expiry dates, and a list of UNREAD fields.

## Entry point
```bash
python -m dogwatch.skills.certificate_reader --help
```

## Safety notes
The model never sees a raw identifier. Dates come from verified quotes parsed by code. A failed quote makes the field UNREAD.

This skill is loaded by the Dogwatch Officer of the Watch and by any agent that reads SKILL.md folders.
