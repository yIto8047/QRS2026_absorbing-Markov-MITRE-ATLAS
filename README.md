# QRS2026 Supplementary Materials

This repository contains supplementary materials for the paper:

"Unraveling AI Threat Scenarios with MITRE ATLAS:
A Probabilistic Risk Analysis Using Absorbing Markov Chains"

## Overview

This repository provides the experimental datasets, Promptfoo configurations, Modelfiles, and evaluation outputs used in the QRS2026 submission.

The study evaluates multi-stage Prompt Injection attacks using a non-homogeneous absorbing Markov chain framework based on MITRE ATLAS.

In particular, the repository includes:

- Tensor Trust Extraction evaluation datasets
- Promptfoo evaluation configurations
- Experimental result logs
- VR (Verbose Refusal) Modelfiles
- SR (Silent Refusal) Modelfiles
- Usability evaluation outputs

---

# Repository Structure

```text
data/
 ├── tensor_trust_extraction_230.csv
 ├── qrs2026_usability_u4_results.csv

configs/
 ├── extraction_d2.yaml
 ├── extraction_u2.yaml
 ├── extraction_u3.yaml
 ├── promptfoo_usability_u4.yaml

results/
 ├── results_d2.json
 ├── results_u2.json
 ├── results_u3.json

modelfiles/
 ├── VR0.modelfile.d0
 ├── VR1.modelfile.d1
 ├── VR2.modelfile.d2
 ├── VR3.modelfile.d3
 ├── VR4.modelfile.d4
 ├── SR0.modelfile.u0
 ├── SR1.modelfile.u1
 ├── SR2.modelfile.u2
 ├── SR3.modelfile.u3
 ├── SR4.modelfile.u4
