"""Typed output the model must produce. Every field carries a verbatim quote that code checks."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

DocType = Literal["coc", "cec", "endorsement", "bst_pst", "bst_fpff", "pscrb", "aff", "medical",
                  "passport", "cdc", "gmdss", "other"]


class QuotedField(BaseModel):
    value: str = ""
    quote: str = ""


class Extraction(BaseModel):
    doc_type: DocType = "other"
    doc_type_quote: str = ""
    administration: QuotedField = Field(default_factory=QuotedField)
    capacity: QuotedField = Field(default_factory=QuotedField)
    issue_date: QuotedField = Field(default_factory=QuotedField)
    expiry_date: QuotedField = Field(default_factory=QuotedField)
    limitations: QuotedField = Field(default_factory=QuotedField)


SYSTEM = (
    "You read one seafarer document that has already had identifiers replaced by placeholders such as "
    "[[COC_1]]. Return JSON only. For each field give the value and a quote copied exactly from the text. "
    "If a field is not in the text, leave value and quote empty. Never guess a date. Never decide validity."
)
