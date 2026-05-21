# Pro01 B Safe Gemini Research Scripts

These scripts are adapted from the `gemini_chrome_v1.01.zip` reference package.

Important boundary:

- No API key is stored in the scripts.
- Use `GOOGLE_API_KEY` or enter the key interactively.
- Output files record model, response, latency, and usage metadata only.
- Do not commit personal test images or API keys.

## Probe Model Availability

```bash
GOOGLE_API_KEY="..." python3 gemini_model_probe_safe.py
```

## Compare OCR Models

```bash
GOOGLE_API_KEY="..." python3 gemini_ocr_compare_safe.py /path/to/invoice-or-receipt.jpg
```

The Pro01 B browser runtime remains the main demo surface. These scripts are
only for local research and model-routing verification.
