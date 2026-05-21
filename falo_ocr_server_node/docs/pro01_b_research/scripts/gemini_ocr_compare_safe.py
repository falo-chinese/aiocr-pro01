#!/usr/bin/env python3
"""
Safe OCR comparison runner for Pro01 B research.

Usage:
  GOOGLE_API_KEY=... python3 gemini_ocr_compare_safe.py /path/to/invoice.jpg

The script records model, latency, response text, and usage metadata. It never
stores the API key in output files.
"""

from __future__ import annotations

import base64
import getpass
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]

PROMPT = """你是一個高精度的繁體中文 OCR 與憑證結構化提取助手。
請分析圖片中的台灣發票、收據或憑證，並只輸出合法 JSON。
請盡量使用固定欄位：
invoice_number, issued_at, seller_name, seller_tax_id, buyer_name,
buyer_tax_id, subtotal, tax_amount, total_amount, item_description,
review_flags。
不確定請留空或放入 review_flags，不要猜測。"""


def read_api_key() -> str:
    api_key = os.environ.get("GOOGLE_API_KEY", "").strip()
    if api_key:
        return api_key
    return getpass.getpass("Google API Key: ").strip()


def read_image_part(path: Path) -> dict:
    mime_type = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    data = base64.b64encode(path.read_bytes()).decode("utf-8")
    return {
        "inlineData": {
            "mimeType": mime_type,
            "data": data,
        }
    }


def call_gemini(api_key: str, model: str, image_part: dict) -> dict:
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": PROMPT},
                    image_part,
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0,
        },
    }
    data = json.dumps(payload).encode("utf-8")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(argv) < 2:
        print("Usage: python3 gemini_ocr_compare_safe.py /path/to/image")
        return 2

    image_path = Path(argv[1]).expanduser()
    if not image_path.exists():
        print(f"找不到圖片：{image_path}")
        return 2

    api_key = read_api_key()
    if not api_key:
        print("缺少 Google API Key。")
        return 2

    image_part = read_image_part(image_path)
    results = {
        "image_name": image_path.name,
        "image_size": image_path.stat().st_size,
        "image_mime_type": image_part["inlineData"]["mimeType"],
        "models": {},
    }

    for model in MODELS:
        print(f"\n[ocr] {model}")
        started = time.time()
        try:
            result = call_gemini(api_key, model, image_part)
            elapsed = time.time() - started
            text = (
                result.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )
            results["models"][model] = {
                "success": True,
                "elapsed_sec": round(elapsed, 3),
                "reply": text,
                "usage_metadata": result.get("usageMetadata", {}),
            }
            print(f"OK {elapsed:.2f}s")
            print(text.strip())
        except urllib.error.HTTPError as exc:
            elapsed = time.time() - started
            body = exc.read().decode("utf-8", errors="replace")
            results["models"][model] = {
                "success": False,
                "elapsed_sec": round(elapsed, 3),
                "error": f"HTTP {exc.code}",
                "details": body,
            }
            print(f"HTTP {exc.code}: {body}")
        except Exception as exc:
            elapsed = time.time() - started
            results["models"][model] = {
                "success": False,
                "elapsed_sec": round(elapsed, 3),
                "error": str(exc),
            }
            print(f"ERROR: {exc}")
        time.sleep(1)

    output_path = Path("pro01b_ocr_comparison_results_safe.json")
    output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n已輸出：{output_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
