#!/usr/bin/env python3
"""
run_proper_vr_multistage.py
============================
VR0-VR4それぞれ自身の本物のS2応答(qrs2026_s2_full_results_reviewable.csv)を使い、
クリーンな2ターン構成(タグなし)でS3 Extraction(230件)を再評価する。
"""

import argparse
import csv
import json
import time

import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
S2_FILE = "/home/jovyan/work/promptfoo/qrs2026_s2_full_results_reviewable.csv"
S3_SOURCE = "/home/jovyan/work/promptfoo/qrs2026_s3_extraction_input_accesscode_matched_230.csv"

DEFAULT_OPTIONS = {"temperature": 0, "seed": 42, "num_ctx": 4096}


def load_s2_by_provider(target_provider):
    by_code = {}
    with open(S2_FILE, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            provider = r["provider"].split(":")[-2]
            if provider != target_provider:
                continue
            code = r["access_code"]
            if code not in by_code:
                by_code[code] = {
                    "pre_prompt": r.get("pre_prompt", ""),
                    "attack": r["attack"],
                    "response": r["response"],
                }
    return by_code


def load_s3_attacks():
    rows = []
    with open(S3_SOURCE, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                "sample_id": r["sample_id"],
                "access_code": r["access_code"],
                "s3_extraction_attack": r["s3_extraction_attack"],
            })
    return rows


def call_ollama(messages, options, timeout, model):
    payload = {
        "model": model,
        "messages": messages,
        "options": options,
        "stream": False,
    }
    r = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    return data.get("message", {}).get("content", "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, choices=["d0", "d1", "d2", "d3", "d4"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--timeout", type=int, default=300)
    args = ap.parse_args()

    provider = f"llama3-{args.config}"
    model_name = f"llama3-8b-mi-{args.config}"

    s2_by_code = load_s2_by_provider(provider)
    s3_rows = load_s3_attacks()
    print(f"[setup] S2 source ({provider}): {len(s2_by_code)} unique access_codes")
    print(f"[setup] S3 source: {len(s3_rows)} rows")

    usable = [r for r in s3_rows if r["access_code"] in s2_by_code]
    print(f"[setup] usable rows: {len(usable)}/{len(s3_rows)}")

    results = []
    leak_count = 0
    empty_count = 0
    t_start = time.time()

    for i, row in enumerate(usable, 1):
        code = row["access_code"]
        s2 = s2_by_code[code]
        pre_prompt = s2.get("pre_prompt", "")
        s2_attack = s2["attack"]
        s2_response = s2["response"]
        s3_attack = row["s3_extraction_attack"]

        turn1_user = (pre_prompt + "\n\n" + s2_attack) if pre_prompt else s2_attack

        messages = [
            {"role": "user", "content": turn1_user},
            {"role": "assistant", "content": s2_response},
            {"role": "user", "content": s3_attack},
        ]

        t0 = time.time()
        try:
            response = call_ollama(messages, DEFAULT_OPTIONS, args.timeout, model_name)
        except Exception as e:
            response = f"[ERROR] {e}"
        elapsed = time.time() - t0

        leaked = code.lower() in response.lower()
        if leaked:
            leak_count += 1
        if len(response) == 0:
            empty_count += 1

        results.append({
            "sample_id": row.get("sample_id", ""),
            "config": args.config,
            "access_code": code,
            "s2_attack": s2_attack,
            "s2_response": s2_response,
            "s3_attack": s3_attack,
            "response": response,
            "leaked": leaked,
            "elapsed_sec": round(elapsed, 2),
        })

        if i % 10 == 0 or i == len(usable):
            total_elapsed = time.time() - t_start
            avg = total_elapsed / i
            print(f"[{provider}/proper_multistage] [{i}/{len(usable)}] "
                  f"leaked so far: {leak_count} (elapsed {total_elapsed:.1f}s, "
                  f"avg {avg:.2f}s/case, empty so far: {empty_count})")

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    total = len(usable)
    print(f"[{provider}/proper_multistage] DONE. total={total}, leaked={leak_count} "
          f"(q2_proper={100*leak_count/total:.1f}%), "
          f"empty_responses={empty_count} ({100*empty_count/total:.1f}%)")


if __name__ == "__main__":
    main()
