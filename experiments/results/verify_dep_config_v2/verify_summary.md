# Failing-state verification — dependency / config

| Category | cases | verified failing | CI green (anomaly) | of which injection changed nothing | inconclusive |
|---|---|---|---|---|---|
| dependency | 35 | 35 | 0 | 0 | 0 |
| config | 5 | 5 | 0 | 0 | 0 |

CI conclusions: {'failure': 39, 'no_run': 1}

## Context controls (clean state + context_requirements, must be green)

| Case | control CI | run |
|---|---|---|
| dep_012 | success | 45603614362 |
| dep_018 | success | 45603689478 |
| dep_025 | success | 45603901073 |
| dep_048 | success | 45604573353 |

## Cases that are NOT verified failing

| Case | CI | run | notes |
|---|---|---|---|
