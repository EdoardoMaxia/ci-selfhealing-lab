# F2 rerun — corrected benchmark (78 cases, --failing-state)

Included cases: 78 (dependency 35, config 4, test 39); excluded: 72 (experiments/excluded_cases.json).
F2 files: 18; A2 files (test baseline): 6.

## Corrections applied (harness errors; raw CSVs unchanged)

| Arm | Model | Case | Action | Reason |
|---|---|---|---|---|
| baseline | openai_gpt4o | dep_002 | success | harness error after a successful repair: CI green on the fix commit at attempt 1, then PR creation failed with GitHub 422 'A pull request already exists' (POST retried by PyGithub's default GithubRetry) |
| both | ollama_qwen3coder_30b | dep_042 | drop | harness error: GitHub 422 'Reference update failed' while creating the attempt-2 fix branch; the run stopped before attempt 2 reached the CI, so its outcome is unknown |

## Baseline, no memory (dependency + config: F2; test: A2)

| Model | dependency | config | test | **total** | SR % | router acc. % |
|---|---|---|---|---|---|---|
| anthropic_haiku | 30/35 | 3/4 | 37/39 | **70/78** | 89.7 | 94.9 |
| openai_gpt4o | 30/35 | 3/4 | 37/39 | **70/78** | 89.7 | 94.9 |
| ollama_qwen38_27b | 30/35 | 3/4 | 38/39 | **71/78** | 91.0 | 97.4 |
| ollama_qwen3coder_30b | 19/34 | 1/4 | 27/39 | **47/77** | 61.0 | 92.2 |
| ollama_llama8b | 15/35 | 0/4 | 19/39 | **34/78** | 43.6 | 88.5 |
| ollama_mistral7b | 6/35 | 0/4 | 18/39 | **24/78** | 30.8 | 83.3 |

## Memory arm (Haiku = calibration, others read-only)

| Model | dependency | config | test | **total** | SR % | router acc. % |
|---|---|---|---|---|---|---|
| anthropic_haiku | 30/35 | 3/4 | 38/39 | **71/78** | 91.0 | 94.9 |
| openai_gpt4o | 30/35 | 3/4 | 38/39 | **71/78** | 91.0 | 96.2 |
| ollama_qwen38_27b | 30/35 | 3/4 | 38/39 | **71/78** | 91.0 | 97.4 |
| ollama_qwen3coder_30b | 20/34 | 3/4 | 27/39 | **50/77** | 64.9 | 90.9 |
| ollama_llama8b | 15/35 | 0/4 | 22/39 | **37/78** | 47.4 | 88.5 |
| ollama_mistral7b | 6/35 | 0/4 | 16/39 | **22/78** | 28.2 | 83.3 |

## Memory effect (paired valid cases)

| Model | n paired | no-mem SR % | mem SR % | Δ pp | b (gained) | c (lost) | McNemar p |
|---|---|---|---|---|---|---|---|
| anthropic_haiku | 78 | 89.7 | 91.0 | +1.28 | 1 | 0 | 1.000 |
| openai_gpt4o | 78 | 89.7 | 91.0 | +1.28 | 1 | 0 | 1.000 |
| ollama_qwen38_27b | 78 | 91.0 | 91.0 | +0.00 | 0 | 0 | 1.000 |
| ollama_qwen3coder_30b | 77 | 61.0 | 64.9 | +3.90 | 4 | 1 | 0.375 |
| ollama_llama8b | 78 | 43.6 | 47.4 | +3.85 | 3 | 0 | 0.250 |
| ollama_mistral7b | 78 | 30.8 | 28.2 | -2.56 | 1 | 3 | 0.625 |

## Skipped included cases, by reason (expected: none)

None: every included case had a red pre-check and was run.

## Timeouts / errors after a red pre-check (counted as failures)

| Arm | Model | Case | Status | Message |
|---|---|---|---|---|
| memory | ollama_llama8b | test_016 | timeout | TIMEOUT |

## Duration

| Step | start | minutes | exit |
|---|---|---|---|
| base_haiku_dependency | 25/11 15:22 | 70 | 0 |
| base_haiku_config | 25/11 16:31 | 8 | 0 |
| base_gpt4o_dependency | 25/11 16:40 | 73 | 0 |
| base_gpt4o_config | 25/11 17:52 | 9 | 0 |
| base_qwen38-4k_dependency | 25/11 18:01 | 87 | 0 |
| base_qwen38-4k_config | 25/11 19:28 | 11 | 0 |
| base_qwen3coder-4k_dependency | 25/11 19:39 | 86 | 0 |
| base_qwen3coder-4k_config | 25/11 21:05 | 11 | 0 |
| base_llama31-4k_dependency | 25/11 21:16 | 92 | 0 |
| base_llama31-4k_config | 25/11 22:48 | 12 | 0 |
| base_mistral-4k_dependency | 25/11 23:00 | 97 | 0 |
| base_mistral-4k_config | 26/11 00:36 | 12 | 0 |
| calib_haiku | 26/11 00:48 | 135 | 0 |
| ro_gpt4o | 26/11 03:03 | 139 | 0 |
| ro_qwen38-4k | 26/11 05:22 | 166 | 0 |
| ro_qwen3coder-4k | 26/11 08:08 | 185 | 0 |
| ro_llama31-4k | 26/11 11:13 | 205 | 0 |
| ro_mistral-4k | 26/11 14:38 | 198 | 0 |

Wall clock: 26.6 h (25/11 15:22 → 26/11 17:56); sum of the steps: 26.6 h.

