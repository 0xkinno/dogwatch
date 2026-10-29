"""Read one OCR text file into typed fields with verified quotes. Needs NEBIUS_API_KEY for the Super call."""
import argparse
import json

from ..bosun.read import read_text
from ..vault.placeholders import Registry


def main(argv=None):
    ap = argparse.ArgumentParser(prog="certificate-reader")
    ap.add_argument("text_file")
    ap.add_argument("--admin", default="default")
    a = ap.parse_args(argv)
    raw = open(a.text_file, encoding="utf-8").read()
    r = read_text(raw, registry=Registry(), doc_id="doc", administration_hint=a.admin)
    print(json.dumps({"doc_type": r.document.doc_type, "expiry": str(r.document.expiry),
                      "unread": r.unread_fields, "quotes_refused": r.quotes_refused}, indent=2))


if __name__ == "__main__":
    main()
