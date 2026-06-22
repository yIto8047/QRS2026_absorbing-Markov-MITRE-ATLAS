# Supplementary Materials: Unraveling Multi-Stage AI Threat Scenarios with MITRE ATLAS

Supplementary datasets, Modelfile configurations, and evaluation scripts for:

> Y. Ito, T. Saito, R. Sasaki, "Unraveling Multi-Stage AI Threat Scenarios with MITRE ATLAS: A Probabilistic Risk Analysis Using Absorbing Markov Chains," QRS 2026 (CFSE Workshop), Springer LNCS.

## Repository structure

```
data/
  exp0_honeypot/            Honeypot logs and S1 request-type breakdown
  exp1_single_stage/        EXP-1: single-stage Hijacking (q1), VR0-VR4
  exp2_multistage_vr/       EXP-2: multi-stage Chain C (q2), VR0-VR4, corrected
  exp3_fewshot_ablation/    EXP-3: few-shot ablation + CIL/RIL classification
  exp4_multistage_sr/       EXP-4: multi-stage Chain C, SR0-SR4, corrected
  exp5_usability/           EXP-5: security-usability evaluation, VR4/SR4 (+/- guardrail)
  exp6_guardrail/           EXP-6: three-layer external guardrail
  source/                   Input datasets (with sha256 checksums)
scripts/                    Evaluation and data-reconstruction scripts
archive_superseded/         Pre-correction data, kept for transparency (see its own README)
```

## Data dictionary

### `data/exp2_multistage_vr/` — EXP-2, Table 3

| File | Config | n | Description |
|---|---|---|---|
| `results_d0_proper.json` | VR0 | 230 | Genuine multi-turn S2->S3, leak rate 67.4% |
| `results_d1_proper.json` | VR1 | 230 | Leak rate 50.0% |
| `results_d2_proper.json` | VR2 | 230 | Leak rate 43.9% |
| `results_d3_proper.json` | VR3 | 230 | Leak rate 20.0% |
| `results_d4_proper.json` | VR4 | 230 | Leak rate 18.7% |

Defense hardening improves multi-stage robustness monotonically (no reversal).

### `data/exp3_fewshot_ablation/` — EXP-3, Table 4

| File | Config | n | Description |
|---|---|---|---|
| `results_d3nofs_proper.json` | VR3 without few-shot | 230 | Leak rate 44.3% |
| `results_d4nofs_proper.json` | VR4 without few-shot | 230 | Leak rate 34.8% |

Compared against `results_d3_proper.json` / `results_d4_proper.json` above (with few-shot). Few-shot substantially lowers total leakage but raises the RIL share of residual leakage.

### `data/exp4_multistage_sr/` — EXP-4, Table 6

| File | Config | n | Description |
|---|---|---|---|
| `s2_u0_results.csv` ... `s2_u4_results.csv` | SR0-SR4 | 776 each | Newly collected, genuine SR Hijacking (S2) responses — did not exist prior to this correction |
| `results_u0_proper.json` ... `results_u4_proper.json` | SR0-SR4 | 230 each | Multi-stage S2->S3 using the genuine SR S2 responses above. Leak rates 70.4% (SR0) -> 17.8% (SR4) |

### `data/exp5_usability/` — EXP-5, Table 7

| File | Config | n | Description |
|---|---|---|---|
| `usability_d4_noguard.json` | VR4, no guardrail | 20 | Overblocking 5.0% |
| `usability_u4_noguard.json` | SR4, no guardrail | 20 | Overblocking 35.0% |
| `usability_d4_guard.json` | VR4 + LLMGuard | 20 | Overblocking unchanged at 5.0% (input/output scanners don't act on benign prompts) |
| `usability_u4_guard.json` | SR4 + LLMGuard | 20 | Overblocking unchanged at 35.0% |

### `data/exp6_guardrail/` — EXP-6, Table 8

| File | Config | n | Description |
|---|---|---|---|
| `multistage_d0_guard.json` | VR0 + guardrail | 230 | Attack coverage 95.7% |
| `multistage_d4_guard.json` | VR4 + guardrail | 230 | Attack coverage 99.6% (strongest overall) |
| `multistage_u0_guard.json` | SR0 + guardrail | 230 | Attack coverage 95.7% |
| `multistage_u4_guard.json` | SR4 + guardrail | 230 | Attack coverage 98.7% |
| `layer1_s3_only.json` | Layer 1 alone (input scanner only) | 230 | Block rate 94.8%, FPR 0% |

Each file with a `provenance` field records the run timestamp, dataset path, dataset sha256, and script used — see file contents for exact values.

### `data/source/`

| File | sha256 | Used by |
|---|---|---|
| `qrs2026_s3_extraction_230_multistage.csv` | `759437fe6db5e772e7cd29172eeff536bf4bfd1f7abd023e0785c1755332b8d0` | EXP-6 guardrail evaluation |
| `qrs2026_usability_test_20.csv` | `2dfb0be247aa9f670670c0a86bbc73eacdf80b9ed934548de399c4335e61e90e` | EXP-5 usability evaluation |

## Scripts

| Script | Purpose |
|---|---|
| `run_proper_vr_multistage.py` | Rebuilds EXP-2 (VR0-VR4 multi-stage) using each configuration's genuine S2 response |
| `run_proper_vr_multistage_ablation.py` | Builds the EXP-3 few-shot-ablation variants (VR3nofs, VR4nofs) |
| `run_s2_sr_collection.py` | Collects new, genuine S2 Hijacking responses for SR0-SR4 (776 scripts each) |
| `run_proper_sr_multistage.py` | Rebuilds EXP-4 (SR0-SR4 multi-stage) using the genuine SR S2 responses |
| `run_guardrail_multistage.py` | EXP-6: applies Layer 1 (PromptInjection scanner) to the S3 turn only, then the model, then Layer 3 (Sensitive scanner) to the response |
| `build_proper_vr_multistage.py` | Helper for constructing genuine two-turn (S2 response + S3 attack) conversation inputs |

## Modelfile configurations

VR0-VR4 (Verbose Refusal) and SR0-SR4 (Silent Refusal) Modelfile definitions are described in the paper, Table 5. Both paradigms share the same four incremental components (SYSTEM policy, TEMPLATE separation, few-shot examples, PARAMETER control); only the refusal style differs (explanatory vs. silent).

## Citation

If you use this data, please cite the paper above. See `archive_superseded/README.md` for details on the data-construction issue and correction if you are comparing against an earlier (pre-correction) copy of this repository.
