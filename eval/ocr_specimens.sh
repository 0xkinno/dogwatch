#!/usr/bin/env bash
# OCR every specimen with Tesseract (WSL or Linux). Output: eval/specimens/*.txt
cd "$(dirname "$0")/specimens"
for f in S*.png; do tesseract "$f" "${f%.png}" --psm 6 >/dev/null 2>&1; done
ls *.txt | wc -l
