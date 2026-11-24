# MIB-12: Maliki Inheritance Benchmark and Reference Oracle

**Author:** Salma Ammari, National Higher School of Islamic Sciences (Dar Al-Quran), Djamaa El Djazair, Algeria

Supplementary material for:
**S. Ammari, "Evaluating Electronic Inheritance Calculation Software in Light of Maliki Jurisprudence: A Madhab-Aware Benchmark and Reference Oracle", IMAN 2026.**

## Contents
| File | Description |
|---|---|
| `faraid_oracle.py` | Madhab-parameterized reference engine (Maliki later practice, Maliki early view, Hanafi, Hanbali) with exact rational arithmetic and an explainable trace. Running it validates the oracle and prints the madhab-sensitivity matrix. |
| `mib12_benchmark.json` | The twelve cases, their Maliki keys and the solutions (base, units, shares, trace) under every profile. |
| `prompt_ar.txt` / `prompt_en.txt` | The exact prompt submitted to the LLM chatbots and its English translation. |
| `results_case_level.csv` | Case-level results of the pilot sample (Pass or error class E1-E5). |
| `results_scores.csv` | DA, MFI, ICS, TDS and JTQ under the paper's weights and two alternative weightings. |

## Usage
```
python3 faraid_oracle.py
```
Requires Python 3.10 or later; no external library.

## Error classes
E1 madhab leakage · E2 special-case failure · E3 share or arithmetic error · E4 impediment blindness · E5 non-disclosure.

## How to cite
Ammari, S. (2026). Evaluating electronic inheritance calculation software in light of Maliki jurisprudence: A madhab-aware benchmark and reference oracle. *14th International Conference on Islamic Applications in Computer Science and Technologies (IMAN 2026)*, Malaysia.

## Licence
© 2026 Salma Ammari. Licensed under **CC BY-NC 4.0** (attribution required, non-commercial use only).
Commercial use, including in commercial software or applications, requires the author's prior written permission: salma93ammari@gmail.com
