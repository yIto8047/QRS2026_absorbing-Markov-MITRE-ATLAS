#!/usr/bin/env python3
import csv

S2_FILE = '/home/jovyan/work/promptfoo/qrs2026_s2_full_results_reviewable.csv'
S3_SOURCE = '/home/jovyan/work/promptfoo/qrs2026_s3_extraction_input_accesscode_matched_230.csv'

def load_s2_by_provider():
    by_provider = {}
    with open(S2_FILE, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for r in reader:
            provider = r['provider'].split(':')[-2]
            code = r['access_code']
            if provider not in by_provider:
                by_provider[provider] = {}
            if code not in by_provider[provider]:
                by_provider[provider][code] = {
                    'pre_prompt': r.get('pre_prompt',''),
                    'attack': r['attack'],
                    'response': r['response'],
                }
    return by_provider

def load_s3_attacks():
    rows = []
    with open(S3_SOURCE, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                'sample_id': r['sample_id'],
                'access_code': r['access_code'],
                's3_extraction_attack': r['s3_extraction_attack'],
            })
    return rows

s2_by_provider = load_s2_by_provider()
print("S2応答モデル一覧:", list(s2_by_provider.keys()))
for p, d in s2_by_provider.items():
    print(f"  {p}: ユニークaccess_code数={len(d)}")

s3_rows = load_s3_attacks()
print(f"\nS3攻撃: {len(s3_rows)}件")

for d_id in ['llama3-d0','llama3-d1','llama3-d2','llama3-d3','llama3-d4']:
    s2_data = s2_by_provider.get(d_id, {})
    matched = sum(1 for r in s3_rows if r['access_code'] in s2_data)
    print(f"  {d_id}: 230件中 {matched}件 マッチ")
