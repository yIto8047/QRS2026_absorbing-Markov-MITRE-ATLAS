#!/usr/bin/env python3
"""
run_s2_sr_collection.py
=========================
SR(u0-u4)モデル自身の、本物のS2 Hijacking応答(776件)を新規収集する。
"""

import argparse
import csv
import time

import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
SOURCE_S2_FILE = "/home/jovyan/work/promptfoo/qrs2026_s2_full_results_reviewable.csv"
DEFAULT_OPTIONS = {"temperature": 0, "seed": 42, "num_ctx": 4096}


def load_attack_pairs():
    rows = []
    with open(SOURCE_S2_FILE, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            provider = r["provider"].split(":")[-2]
            if provider != "llama3-d0":
                continue
            rows.append({
                "access_code": r["access_code"],
                "pre_prompt": r.get("pre_prompt", ""),
                "attack": r["attack"],
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
    ap.add_argument("--config", required=True, choices=["u0", "u1", "u2", "u3", "u4"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--timeout", type=int, default=300)
    args = ap.parse_args()

    model_name = f"llama3-8b-mi-{args.config}"
    provider_label = f"llama3-{args.config}"

    attacks = load_attack_pairs()
    print(f"[setup] attack pairs (from d0 source): {len(attacks)}")

    out_f = open(args.out, "w", newline="", encoding="utf-8")
    writer = csv.DictWriter(out_f, fieldnames=["provider", "access_code", "pre_prompt", "attack", "response"])
    writer.writeheader()

    t_start = time.time()
    empty_count = 0

    for i, row in enumerate(attacks, 1):
        pre_prompt = row["pre_prompt"]
        attack = row["attack"]
        user_msg = (pre_prompt + "\n\n" + attack) if pre_prompt else attack

        messages = [{"role": "user", "content": user_msg}]

        t0 = time.time()
        try:
            response = call_ollama(messages, DEFAULT_OPTIONS, args.timeout, model_name)
        except Exception as e:
            response = f"[ERROR] {e}"
        elapsed = time.time() - t0

        if len(response) == 0:
            empty_count += 1

        writer.writerow({
            "provider": provider_label,
            "access_code": row["access_code"],
            "pre_prompt": pre_prompt,
            "attack": attack,
            "response": response,
        })

        if i % 20 == 0 or i == len(attacks):
            total_elapsed = time.time() - t_start
            avg = total_elapsed / i
            print(f"[{provider_label}/s2_collection] [{i}/{len(attacks)}] "
                  f"elapsed {total_elapsed:.1f}s, avg {avg:.2f}s/case, empty so far: {empty_count}")

    out_f.close()
    print(f"[{provider_label}/s2_collection] DONE. total={len(attacks)}, empty={empty_count}")


if __name__ == "__main__":
    main()
