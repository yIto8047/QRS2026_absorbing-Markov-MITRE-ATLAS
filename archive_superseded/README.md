# Archive: superseded pre-correction data

These files were superseded during final verification before publication, due to a
data-construction issue described in the paper's Conclusion. They are kept here
(not deleted) for transparency, so the nature of the issue can be inspected directly
rather than taken only on the authors' word. **Do not use these for any analysis** —
use the corresponding files in `data/` instead.

## What was wrong

The multi-turn evaluation input for the S2 (Hijacking) -> S3 (Extraction) chained
attack scenario is built from two parts: the model's own S2-stage response (used as
the prior conversational turn) and the new S3 extraction attempt. For every
configuration other than the VR0 baseline, the S2 response actually used was drawn
from a single shared model run (VR0's own run) rather than from each configuration's
own genuine response. In addition, for the Silent Refusal (SR) paradigm, no
first-party S2 Hijacking response data existed at all until it was newly collected
as part of this correction (see `data/exp4_multistage_sr/s2_u*_results.csv`).

This produced an apparent reversal in which the most hardened configuration (VR4)
appeared weakest under multi-stage evaluation despite being strongest under
single-stage Hijacking evaluation — reported as a central finding in an earlier,
pre-correction draft of the paper. After reconstructing all results using each
configuration's own genuine multi-turn S2 response, this reversal did not replicate.

## File-by-file

| File | Problem |
|---|---|
| `extraction_d0_guard.json`, `extraction_d4_guard.json`, `extraction_u0_guard.json`, `extraction_u4_guard.json` | Guardrail evaluation built on the contaminated input CSV below; Layer 1 was also applied to the full concatenated S2+S3 string rather than the S3 turn alone, producing an artificial 100% block rate for every configuration |
| `extraction_base_layer1only.json` | Same issue, base `llama3:8b` model |
| `extraction_d4_noguard.json`, `extraction_u4_noguard.json` | Unguarded baseline built on the same contaminated CSV; reports VR4 leak rate 41.3% and SR4 leak rate 7.0%, both wrong (correct values: 18.7% and 17.8% — see `data/exp2_multistage_vr/` and `data/exp4_multistage_sr/`) |
| `qrs2026_s3_extraction_input_accesscode_matched_230.csv` | Root cause: the S3 input dataset with VR0's S2 response embedded for all configurations |
| `results_u0.json` ... `results_u4.json` (no `_proper` suffix) | Early SR multi-stage attempt, built before genuine SR S2 Hijacking data existed |

## What is unaffected

EXP-0 (honeypot) and EXP-1 (single-stage Hijacking, q1) do not depend on S2-response
context and are not affected by this issue. The three-layer guardrail *mechanism*
(Layer 1 / Layer 2 / Layer 3) itself is also unaffected — only its input construction
was corrected; see `scripts/run_guardrail_multistage.py` for the corrected version.
