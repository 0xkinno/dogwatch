#!/usr/bin/env python3
"""Curl every public route and /api/status on the deployed URLs and fail on any non-200.
Usage: python scripts/reachability.py [web_url] [api_url]"""
import sys
import urllib.request

WEB = sys.argv[1] if len(sys.argv) > 1 else "https://dogwatch-eight.vercel.app"
API = sys.argv[2] if len(sys.argv) > 2 else "https://dogwatch-api.vercel.app"
ROUTES = ["/", "/watch", "/contract", "/outbox", "/boundary", "/proof", "/judge", "/how"]
bad = 0
for base, paths in ((WEB, ROUTES), (API, ["/api/status", "/api/stats", "/api/boundary", "/api/proof/p7_conventions"])):
    for p in paths:
        try:
            code = urllib.request.urlopen(urllib.request.Request(base + p, headers={"User-Agent": "dogwatch-reachability"}), timeout=60).status
        except Exception as e:
            code = getattr(e, "code", type(e).__name__)
        print(code, base + p)
        bad += code != 200
sys.exit(1 if bad else 0)
