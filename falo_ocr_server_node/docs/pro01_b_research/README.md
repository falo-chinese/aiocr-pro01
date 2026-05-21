# Pro01 B Version Notes

Last updated: 2026-05-21

## Reference Package

This B version now references the local package:

```text
/Users/force/Downloads/gemini_chrome_v1.01.zip
```

The reference package contributed three practical directions:

- Gemini 3.1 Flash-Lite + Gemini 3.5 Flash as the B version dual-route baseline.
- Browser-side WebP 768 image preprocessing as the default send-image strategy.
- Model comparison records for latency, OCR differences, and follow-up accuracy analysis.

The original package also included local test scripts with an API key embedded in source code. Those files were not copied as-is. Pro01 B keeps only safe versions under `scripts/`, where the key must come from `GOOGLE_API_KEY` or interactive input.

## Version Boundary

This folder documents the B version direction.

- A version remains at `client_demo/viewer_prompt_lab/index.html`.
- B version is created separately at `client_demo/viewer_prompt_lab_b/index.html`.
- B version uses separate localStorage / IndexedDB keys so it does not overwrite A version browser memory.

## B Version Model Route

B version keeps two route presets for OCR comparison:

```text
Default dual route:
A1: gemini-2.5-flash
A2: gemini-3.1-flash-lite

Enhanced dual route:
A1: gemini-3.1-flash-lite
A2: gemini-3.5-flash
```

The default route is designed for low-cost baseline comparison between the 2.5 generation and the 3.1 Flash-Lite route. The enhanced route remains available when the user wants a stronger second opinion.

## B Version Image Sending Default

B version uses browser-side image optimization as the default before sending an image to Gemini:

```text
Default image mode: WebP 768 OCR
Conversion runtime: browser Canvas, local only
Output format: image/webp
Max long side: 768 px
Quality: 0.85
Upscaling: no
```

The purpose is to reduce Gemini vision tile / token cost while keeping the document readable enough for invoice, receipt, business-card, and form OCR tasks. The original upload is still treated as the source evidence, and the runtime records both sides:

```text
source_image_meta: original type / size / width / height
last_send_image_meta: sent type / size / width / height / strategy / quality
```

Users can still switch to original file, JPG, standard PNG, or high-quality PNG from the system settings tab when a specific test needs more visual detail.

## Imported Research Files

```text
ocr_comparison_dashboard.html
ocr_technical_synthesis.md
ocr_comparison_results.json
scripts/gemini_model_probe_safe.py
scripts/gemini_ocr_compare_safe.py
```

These files are reference material for cost / routing / OCR architecture discussion. They are not treated as the canonical Pro01 runtime source.

## Design Intent

The B version is for testing a smarter dual-route model strategy:

```text
invoice / receipt image
-> default A1 Gemini 2.5 Flash baseline
-> default A2 Gemini 3.1 Flash-Lite low-cost candidate
-> optional enhanced route: A1 Gemini 3.1 Flash-Lite / A2 Gemini 3.5 Flash
-> human reconciliation
-> confirmed record
-> analysis package
```

This keeps the HITL principle: AI proposals remain draft evidence until human confirmation.
