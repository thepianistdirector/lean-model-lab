# Sources, candidate tools and data policy

Official entry points inspected while preparing this plan on 2026-09-07. These links support the bounded descriptions below; they do not prove an implemented integration, available benchmark data, endorsement or scientific validity for every planned scenario.

| Source | Supported planning use |
| --- | --- |
| [llama.cpp](https://github.com/ggml-org/llama.cpp) | Official local inference project; candidate backend, including Apple Silicon support. A capability listing is not a performance result. |
| [PyTorch profiler](https://docs.pytorch.org/docs/stable/profiler.html) | Official profiling API reference for instrumenting software runs. |
| [vLLM benchmarks](https://docs.vllm.ai/en/stable/api/vllm/benchmarks/index.html) | Official benchmark entry points for later latency/throughput comparisons. |
| [MLCommons benchmarks](https://mlcommons.org/benchmarks/) | Benchmark methodology reference; this project is not an official MLPerf submission or affiliated benchmark. |

## Before adopting a dependency or dataset

Record the exact official release and license, maintenance/advisory state, runtime and transitive dependencies, safe loading behavior, telemetry/network use, storage/compute cost, alternatives and rollback. A source being listed here does not authorize installation or data download. Exact versions are deliberately deferred until the implementation environment and compatibility evidence exist.

For each dataset/model, document provenance, permitted use, attribution, redistribution rights, access requirements, geography/population/time coverage, uncertainty and missing variables. Link source records to all derived artifacts. Reject incompatible terms and use an honestly labeled synthetic fixture when appropriate. Keep private information, credentials, controlled-access data and third-party assets out of this public repository.

## Evidence limits

Evaluate PyTorch profiling for training instrumentation and llama.cpp for an initial local inference adapter; vLLM is a later serving adapter when suitable hardware and an approved environment exist. MLPerf methodology is a reference for controlled comparisons, not a certification claim. Exact model weights, training data and backend versions require separate rights/security review.

Official tool documentation establishes the tool's stated purpose; our model cards and independent benchmarks must establish applicability to our experiment. Sources are not blanket proof for results we have not measured. The project's original documents use AGPL-3.0-only; referenced material retains its own terms.
