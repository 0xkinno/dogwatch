"""Arjun Menon: the demonstration profile. Every value here is invented for the demonstration."""
from __future__ import annotations

ARJUN = {
    "name": "Arjun Menon",
    "role": "Second Officer, product tanker",
    "documents": [
        {"id": "coc", "doc_type": "coc", "administration": "India", "label": "Certificate of Competency (India)", "expiry": "2029-06-30"},
        {"id": "cec", "doc_type": "endorsement", "administration": "Singapore", "label": "Certificate of Equivalent Competency (Singapore)", "expiry": "2029-06-30", "endorsement": "cec"},
        {"id": "oil", "doc_type": "endorsement", "administration": "India", "label": "Oil tanker endorsement", "expiry": "2029-06-30", "endorsement": "oil_tanker"},
        {"id": "medical", "doc_type": "medical", "administration": "India", "label": "Medical fitness certificate", "expiry": "2027-03-14"},
        {"id": "passport", "doc_type": "passport", "administration": "India", "label": "Passport", "expiry": "2031-05-02"},
        {"id": "bst", "doc_type": "bst", "administration": "India", "label": "Basic safety training refresher", "expiry": "2028-11-20"},
    ],
    "ledger": [
        {"sign_on": "2025-03-05", "sign_off": "2025-09-18", "vessel": "MT Specimen One", "flag": "SG", "capacity": "Second Officer", "ship_type": "oil_tanker"},
        {"sign_on": "2026-01-12", "sign_off": "2026-07-30", "vessel": "MT Specimen Two", "flag": "SG", "capacity": "Second Officer", "ship_type": "oil_tanker"},
    ],
}

CONTRACT_OFFER = {
    "start": "2027-02-01",
    "end": "2027-07-31",
    "travel_before": 0,
    "travel_after": 0,
    "required_types": ["coc", "medical", "passport", "bst"],
}

DEMO_TODAY = "2026-10-28"
