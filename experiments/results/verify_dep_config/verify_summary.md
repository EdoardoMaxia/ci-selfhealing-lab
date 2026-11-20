# Failing-state verification — dependency / config

| Category | cases | verified failing | CI green (anomaly) | of which injection changed nothing | inconclusive |
|---|---|---|---|---|---|
| dependency | 50 | 31 | 19 | 0 | 0 |
| config | 50 | 2 | 47 | 46 | 1 |

CI conclusions: {'success': 66, 'error': 1, 'failure': 33}

## Cases that are NOT verified failing

| Case | CI | run | notes |
|---|---|---|---|
| conf_001 | success | 44744236984 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_002 | success | 44744244107 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_003 | success | 44744253882 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_004 | success | 44744260884 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_005 | success | 44744268188 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_006 | error | 44744387397 | run did not complete within --ci-timeout |
| conf_007 | success | 44744394833 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_008 | success | 44744401792 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_009 | success | 44744409759 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_010 | success | 44744418067 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_011 | success | 44746251187 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_012 | success | 44746258508 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_014 | success | 44746280970 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_015 | success | 44746289150 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_016 | success | 44746409565 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_017 | success | 44746417728 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_018 | success | 44746426298 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_019 | success | 44746436233 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_020 | success | 44746444363 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_021 | success | 44746560136 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_022 | success | 44746567387 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_023 | success | 44746576303 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_024 | success | 44746583022 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_025 | success | 44746592535 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_026 | success | 44746711442 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_027 | success | 44746719267 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_028 | success | 44746727401 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_029 | success | 44746735732 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_030 | success | 44746743617 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_032 | success | 44746877593 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_033 | success | 44746885357 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_034 | success | 44746895348 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_035 | success | 44746903629 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_036 | success | 44747019312 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_037 | success | 44747027933 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_038 | success | 44747035129 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_039 | success | 44747045296 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_040 | success | 44747053644 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_041 | success | 44747178290 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_042 | success | 44747185274 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_043 | success | 44747194523 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_044 | success | 44747201890 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_045 | success | 44747210834 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_046 | success | 44747329997 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_047 | success | 44747348795 | ANOMALY: CI green on the injected state |
| conf_048 | success | 44747356318 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_049 | success | 44747364565 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| conf_050 | success | 44747372587 | ANOMALY: CI green on the injected state | injection_noop: inject_error changed no file (state identical to main) |
| dep_010 | success | 44742394353 | ANOMALY: CI green on the injected state |
| dep_012 | success | 44742660778 | ANOMALY: CI green on the injected state |
| dep_013 | success | 44742677948 | ANOMALY: CI green on the injected state |
| dep_016 | success | 44742843602 | ANOMALY: CI green on the injected state |
| dep_017 | success | 44742858505 | ANOMALY: CI green on the injected state |
| dep_018 | success | 44742872353 | ANOMALY: CI green on the injected state |
| dep_019 | success | 44742885671 | ANOMALY: CI green on the injected state |
| dep_021 | success | 44743049460 | ANOMALY: CI green on the injected state |
| dep_024 | success | 44743091378 | ANOMALY: CI green on the injected state |
| dep_025 | success | 44743106703 | ANOMALY: CI green on the injected state |
| dep_026 | success | 44743228455 | ANOMALY: CI green on the injected state |
| dep_028 | success | 44743259257 | ANOMALY: CI green on the injected state |
| dep_034 | success | 44743457823 | ANOMALY: CI green on the injected state |
| dep_035 | success | 44743472808 | ANOMALY: CI green on the injected state |
| dep_039 | success | 44743642433 | ANOMALY: CI green on the injected state |
| dep_041 | success | 44743778672 | ANOMALY: CI green on the injected state |
| dep_043 | success | 44743807599 | ANOMALY: CI green on the injected state |
| dep_046 | success | 44743959451 | ANOMALY: CI green on the injected state |
| dep_048 | success | 44743990164 | ANOMALY: CI green on the injected state |
