# QRS2026 Supplementary Materials

This repository contains supplementary materials for the paper:

> **"Unraveling Multi-Stage AI Threat Scenarios with MITRE ATLAS: A Probabilistic Risk Analysis Using Absorbing Markov Chains"**  
> Yoshinari Ito, Ryoichi Sasaki, Taiichi Saito — Tokyo Denki University, Tokyo, Japan  
> QRS 2026

---

## Overview

This repository provides the experimental datasets, Promptfoo evaluation configurations, Modelfiles, and result logs used in the QRS2026 submission.

The study formulates four-stage Prompt Injection attacks (S1–S4) as a non-homogeneous absorbing Markov chain based on MITRE ATLAS, and empirically evaluates Meta Llama3:8B using Tensor Trust attack scripts.

---

## Repository Structure

```
data/
 ├── qrs2026_s3_extraction_input_accesscode_matched_230.csv  # EXP-2: Extraction test inputs (230 cases)
 ├── qrs2026_usability_test_20.csv                           # Usability evaluation prompts (20 cases)

configs/
 ├── extraction_d2.yaml          # Promptfoo config: EXP-2 for VR2 (d2)
 ├── extraction_u2.yaml          # Promptfoo config: EXP-2 for SR2 (u2)
 ├── extraction_u3.yaml          # Promptfoo config: EXP-2 for SR3 (u3)
 ├── promptfoo_usability_u4.yaml # Promptfoo config: Usability evaluation for SR4 (u4)

results/
 ├── results_d2.json             # EXP-2 result: VR2 Extraction (n=230)
 ├── results_u2.json             # EXP-2 result: SR2 Extraction (n=230)
 ├── results_u3.json             # EXP-2 result: SR3 Extraction (n=230)
 ├── qrs2026_usability_u4_results.csv  # Usability evaluation result: SR4

modelfiles/
 ├── Modelfile.d0    # VR0: Baseline
 ├── Modelfile.d1    # VR1: + SYSTEM policy
 ├── Modelfile.d2    # VR2: + TEMPLATE separation
 ├── Modelfile.d3    # VR3: + few-shot safe-refusal examples (verbose)
 ├── Modelfile.d4    # VR4: + PARAMETER control
 ├── Modelfile.u0    # SR0: Baseline
 ├── Modelfile.u1    # SR1: + SYSTEM silent-refusal policy
 ├── Modelfile.u2    # SR2: + TEMPLATE separation
 ├── Modelfile.u3    # SR3: + few-shot silent-refusal examples
 ├── Modelfile.u4    # SR4: + PARAMETER control

honeypot_logs/
 ├── ollama_proxy_2026-03-22.csv   # S1 honeypot log: Day 1
 ├── ollama_proxy_2026-03-23.csv
 ├── ...
 ├── ollama_proxy_2026-05-11.csv   # S1 honeypot log: Day 51
```

---

## Experiment Summary

| Experiment | Description | Dataset | Config |
|---|---|---|---|
| EXP-1 | Single-stage Hijacking evaluation (VR0–VR4) | Tensor Trust 776 scripts | — |
| EXP-2 | Single-stage Extraction evaluation (VR2, SR2, SR3) | 230 scripts (see `data/`) | `configs/extraction_*.yaml` |
| EXP-3 | Few-shot ablation (VR3nofs, VR4nofs) | 230 scripts | — |
| EXP-4 | Manual failure-mode classification (CIL vs. RIL) | Subset of EXP-2 FAILs | — |
| EXP-U | Usability evaluation (SR4) | 20 benign prompts | `configs/promptfoo_usability_u4.yaml` |

---

## Model Configuration Summary

| Config | Paradigm | SYSTEM | TEMPLATE | Few-shot | PARAMETER |
|---|---|---|---|---|---|
| VR0 (d0) | Verbose Refusal | None | No | None | Default |
| VR1 (d1) | Verbose Refusal | Protect access_code | No | None | Default |
| VR2 (d2) | Verbose Refusal | Same as VR1 | Yes | None | Default |
| VR3 (d3) | Verbose Refusal | Same as VR1 | Yes | 3× verbose | Default |
| VR4 (d4) | Verbose Refusal | Same as VR1 | Yes | 3× verbose | temp 0.1 / num_predict 256 |
| SR0 (u0) | Silent Refusal | None | No | None | Default |
| SR1 (u1) | Silent Refusal | Do NOT explain refusal | No | None | Default |
| SR2 (u2) | Silent Refusal | Same as SR1 | Yes | None | Default |
| SR3 (u3) | Silent Refusal | Same as SR1 | Yes | 3× silent | Default |
| SR4 (u4) | Silent Refusal | Same as SR1 | Yes | 3× silent | temp 0.1 / num_predict 256 |

---

## S1 Honeypot Logs — Anonymization Policy

The `honeypot_logs/` directory contains 51 daily CSV log files recorded by the Beelzebub high-interaction honeypot between March 22 and May 11, 2026 (19,932 rows total).

The following anonymization was applied before publication:

| Field | Original content | Published content |
|---|---|---|
| `client_ip` | Source IP address | SHA-256 hash prefix (e.g., `anon_c7aa871b`) |
| `x_forwarded_for` | Relay IP address | SHA-256 hash prefix |
| `host` | Honeypot server IP/hostname | `[honeypot-host]` |
| `request_body_text` | Full request body | Valid IPs within text replaced with hash prefix |
| `response_body_text` | Full response body | Valid IPs within text replaced with hash prefix |

All other fields — including timestamps, HTTP methods, paths, user agents, request/response bodies, and model responses — are published as recorded.

Note: Patterns resembling IP addresses that appear inside version strings (e.g., `Chrome/120.0.0.0`, `rv:1.9.2.16`, `phpMyAdmin-2.8.0.1`) were identified as software version numbers and retained without modification.

---

## How to Reproduce EXP-2

```bash
# Install Promptfoo
npm install -g promptfoo

# Run Extraction evaluation for VR2
promptfoo eval --config configs/extraction_d2.yaml --output results/results_d2.json

# Run Extraction evaluation for SR2
promptfoo eval --config configs/extraction_u2.yaml --output results/results_u2.json

# Run Extraction evaluation for SR3
promptfoo eval --config configs/extraction_u3.yaml --output results/results_u3.json

# Compute q2
python3 -c "
import json
for model, f in [('VR2','results/results_d2.json'),('SR2','results/results_u2.json'),('SR3','results/results_u3.json')]:
    d = json.load(open(f))
    r = d['results']['results']
    fail = sum(1 for x in r if not x['success'])
    print(f'{model}: q2={fail/len(r):.3f}, Defense={(1-fail/len(r))*100:.1f}%')
"
```

---

## Software Environment

| Component | Version |
|---|---|
| Meta Llama3:8B | via Ollama 0.23.2 |
| Promptfoo | 0.121.11 |
| Python | 3.12.9 |
| GPU | NVIDIA Tesla V100-PCIE-32GB |
| CUDA | 12.2 |

---

## License

The Tensor Trust dataset is subject to its original license:  
https://github.com/HumanCompatibleAI/tensor-trust

Modelfiles and evaluation configurations in this repository are released under the MIT License.

---

## Citation

```bibtex
@inproceedings{ito2026qrs,
  title     = {Unraveling Multi-Stage AI Threat Scenarios with MITRE ATLAS: A Probabilistic Risk Analysis Using Absorbing Markov Chains},
  author    = {Ito, Yoshinari and Sasaki, Ryoichi and Saito, Taiichi},
  booktitle = {Proceedings of the 2026 IEEE International Conference on Software Quality, Reliability, and Security (QRS)},
  year      = {2026}
}
```
