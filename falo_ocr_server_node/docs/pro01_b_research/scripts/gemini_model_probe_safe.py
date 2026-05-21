#!/usr/bin/env python3
"""
Safe Gemini model probe for Pro01 B research.

This script is adapted from the gemini_chrome_v1.01 reference package, but it
does not hard-code any API key. Use GOOGLE_API_KEY or enter the key at runtime.
"""

from __future__ import annotations

import getpass
import json
import os
import sys
import urllib.error
import urllib.request


MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
]


def read_api_key() -> str:
    api_key = os.environ.get("GOOGLE_API_KEY", "").strip()
    if api_key:
        return api_key
    return getpass.getpass("Google API Key: ").strip()


def call_text_probe(api_key: str, model: str) -> dict:
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "請只輸出合法 JSON："
                            "{\"model_test\":\"ok\",\"model\":\"%s\"}" % model
                        )
                    }
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
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    api_key = read_api_key()
    if not api_key:
        print("缺少 Google API Key。")
        return 2

    for model in MODELS:
        print(f"\n[probe] {model}")
        try:
          result = call_text_probe(api_key, model)
        except urllib.error.HTTPError as exc:
          body = exc.read().decode("utf-8", errors="replace")
          print(f"HTTP {exc.code}: {body}")
          continue
        except Exception as exc:
          print(f"ERROR: {exc}")
          continue

        text = (
            result.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )
        usage = result.get("usageMetadata", {})
        print(text.strip())
        print(json.dumps(usage, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
