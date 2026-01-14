#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-image upload test for /api/query/image.
Run with a local server at http://localhost:5000.
"""

import os
import sys
import requests

BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:5000")
IMAGE_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "frontend",
    "static",
    "images",
    "67a99ed6f3db4z2m7bdnw17636.jpg",
)


def build_files(count: int) -> list[tuple[str, object]]:
    files = []
    for _ in range(count):
        files.append(("image", open(IMAGE_PATH, "rb")))
    return files


def main() -> int:
    if not os.path.exists(IMAGE_PATH):
        print(f"Image not found: {IMAGE_PATH}")
        return 1

    files = build_files(3)
    data = {
        "question": "Test multi-image upload",
        "subject": "physics",
        "deep_think": "false",
        "level_override": "auto",
        "use_profile": "false",
    }

    try:
        resp = requests.post(
            f"{BASE_URL}/api/query/image",
            data=data,
            files=files,
            timeout=30,
        )
        print("Status Code:", resp.status_code)
        print(resp.text)
        if not resp.ok:
            return 1
        payload = resp.json()
        if payload.get("status") != "success":
            return 1
        return 0
    finally:
        for _, handle in files:
            handle.close()


if __name__ == "__main__":
    sys.exit(main())
