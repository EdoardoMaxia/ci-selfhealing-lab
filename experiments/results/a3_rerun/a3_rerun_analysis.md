[old] anthropic_haiku/nomemory: benchmark_20260908_151421_anthropic_haiku_nomemory.csv
[old] anthropic_haiku/memory: benchmark_20260909_154930_anthropic_haiku_memory.csv
[new] anthropic_haiku/nomemory: benchmark_20261114_093325_anthropic_haiku_nomemory.csv
[new] anthropic_haiku/memory: benchmark_20261115_081807_anthropic_haiku_memory.csv
[old] openai_gpt4o/nomemory: benchmark_20260908_174703_openai_gpt4o_nomemory.csv
[old] openai_gpt4o/memory: benchmark_20260909_181906_openai_gpt4o_memory.csv
[new] openai_gpt4o/nomemory: benchmark_20261114_135224_openai_gpt4o_nomemory.csv
[new] openai_gpt4o/memory: benchmark_20261115_104053_openai_gpt4o_memory.csv
[old] ollama_qwen38_27b/nomemory: benchmark_20260908_204858_ollama_qwen38_27b_nomemory.csv
[old] ollama_qwen38_27b/memory: benchmark_20260909_212204_ollama_qwen38_27b_memory.csv
[new] ollama_qwen38_27b/nomemory: benchmark_20261114_163352_ollama_qwen38_27b_nomemory.csv
[new] ollama_qwen38_27b/memory: benchmark_20261115_131402_ollama_qwen38_27b_memory.csv
[old] ollama_qwen3coder_30b/nomemory: benchmark_20260909_011420_ollama_qwen3coder_30b_nomemory.csv
[old] ollama_qwen3coder_30b/memory: benchmark_20260910_014632_ollama_qwen3coder_30b_memory.csv
[new] ollama_qwen3coder_30b/nomemory: benchmark_20261114_204523_ollama_qwen3coder_30b_nomemory.csv
[new] ollama_qwen3coder_30b/memory: benchmark_20261115_173004_ollama_qwen3coder_30b_memory.csv
[old] ollama_llama8b/nomemory: benchmark_20260909_042131_ollama_llama8b_nomemory.csv
[old] ollama_llama8b/memory: benchmark_20260910_045945_ollama_llama8b_memory.csv
[new] ollama_llama8b/nomemory: benchmark_20261114_235943_ollama_llama8b_nomemory.csv
[new] ollama_llama8b/memory: benchmark_20261115_204439_ollama_llama8b_memory.csv
[old] ollama_mistral7b/nomemory: benchmark_20260909_091620_ollama_mistral7b_nomemory.csv
[old] ollama_mistral7b/memory: benchmark_20260910_100703_ollama_mistral7b_memory.csv
[new] ollama_mistral7b/nomemory: benchmark_20261115_034957_ollama_mistral7b_nomemory.csv
[new] ollama_mistral7b/memory: benchmark_20261116_004218_ollama_mistral7b_memory.csv

Table 1 - SR % with/without memory (old = paper/September, new = rerun)
| model | SR nomem old | SR nomem new | SR mem old | SR mem new | d mem old | d mem new |
|---|---|---|---|---|---|---|
| anthropic_haiku | 88.67 | 89.33 | 90.00 | 88.67 | +1.33 | -0.67 |
| openai_gpt4o | 83.33 | 82.00 | 83.33 | 84.67 | +0.00 | +2.67 |
| ollama_qwen38_27b | 88.67 | 86.00 | 93.33 | 88.00 | +4.67 | +2.00 |
| ollama_qwen3coder_30b | 69.33 | 74.67 | 72.67 | 76.00 | +3.33 | +1.33 |
| ollama_llama8b | 58.00 | 55.33 | 56.67 | 54.67 | -1.33 | -0.67 |
| ollama_mistral7b | 42.00 | 25.33 | 43.33 | 22.67 | +1.33 | -2.67 |

Table 2 - SR % per category (new run)
| model | depe nomem | depe mem | test nomem | test mem | conf nomem | conf mem |
|---|---|---|---|---|---|---|
| anthropic_haiku | 90.00 | 88.00 | 88.00 | 88.00 | 90.00 | 90.00 |
| openai_gpt4o | 88.00 | 88.00 | 88.00 | 90.00 | 70.00 | 76.00 |
| ollama_qwen38_27b | 88.00 | 88.00 | 86.00 | 90.00 | 84.00 | 86.00 |
| ollama_qwen3coder_30b | 74.00 | 74.00 | 68.00 | 72.00 | 82.00 | 82.00 |
| ollama_llama8b | 50.00 | 48.00 | 60.00 | 62.00 | 56.00 | 54.00 |
| ollama_mistral7b | 26.00 | 20.00 | 40.00 | 40.00 | 10.00 | 8.00 |

Table 3 - successes by attempt, new memory run (fix_attempt = attempt of the successful fix; check the column semantics)
| model | T1 | T2 | T3 | failed | n |
|---|---|---|---|---|---|
| anthropic_haiku | 126 | 7 | 0 | 17 | 150 |
| openai_gpt4o | 106 | 16 | 5 | 23 | 150 |
| ollama_qwen38_27b | 123 | 4 | 5 | 18 | 150 |
| ollama_qwen3coder_30b | 89 | 18 | 7 | 36 | 150 |
| ollama_llama8b | 75 | 6 | 1 | 68 | 150 |
| ollama_mistral7b | 26 | 5 | 3 | 116 | 150 |

Table 4 - cases that received episodes (memory_hits>0)
| model | run | cases w/ episodes | solved | failed |
|---|---|---|---|---|
| anthropic_haiku | old | 15 | 1 | 14 |
| anthropic_haiku | new | 17 | 0 | 17 |
| openai_gpt4o | old | 30 | 6 | 24 |
| openai_gpt4o | new | 27 | 5 | 22 |
| ollama_qwen38_27b | old | 15 | 6 | 9 |
| ollama_qwen38_27b | new | 23 | 5 | 18 |
| ollama_qwen3coder_30b | old | 51 | 10 | 41 |
| ollama_qwen3coder_30b | new | 43 | 7 | 36 |
| ollama_llama8b | old | 62 | 3 | 59 |
| ollama_llama8b | new | 68 | 1 | 67 |
| ollama_mistral7b | old | 74 | 5 | 69 |
| ollama_mistral7b | new | 97 | 3 | 94 |

Table 5 - cross-model transfer (new): memory vs no-memory per case
| model | SR nomem | SR mem | delta | gained | lost |
|---|---|---|---|---|---|
| anthropic_haiku | 89.33 | 88.67 | -0.67 | 0 | 1 |
| openai_gpt4o | 82.00 | 84.67 | +2.67 | 6 | 2 |
| ollama_qwen38_27b | 86.00 | 88.00 | +2.00 | 4 | 1 |
| ollama_qwen3coder_30b | 74.67 | 76.00 | +1.33 | 3 | 1 |
| ollama_llama8b | 55.33 | 54.67 | -0.67 | 1 | 2 |
| ollama_mistral7b | 25.33 | 22.67 | -2.67 | 2 | 6 |
