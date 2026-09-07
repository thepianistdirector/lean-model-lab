# Sources, candidate tools and data policy

Official documentation and primary research inspected for the architecture foundation on 2026-09-07. These sources support the bounded design decisions stated below. They do not prove an implemented integration, available hardware, benchmark result, endorsement or universal scientific rule.

## Benchmark and measurement contracts

| Source | Supported planning use and limit |
| --- | --- |
| [MLCommons Training policies](https://github.com/mlcommons/training_policies/blob/master/training_rules.adoc) | Primary benchmark rules for explicit model/data/quality contracts, cache state, run seeds, whole-run wall-clock boundaries, repeated runs and retaining non-convergence. Lean Model Lab uses the principles; it is not an MLPerf submission. |
| [MLPerf Inference LoadGen](https://github.com/mlcommons/inference/blob/master/loadgen/README.md) | Official workload-generation reference for offline/server modes, offered load and performance/accuracy separation. Its scenarios are design references, not this project's implemented harness. |
| [vLLM serving benchmark CLI](https://docs.vllm.ai/en/stable/cli/bench/serve/) | Official definitions exposed by a candidate serving benchmark, including TTFT, TPOT, ITL, end-to-end latency, percentiles and goodput SLO inputs. This does not establish vLLM as the first backend or make its aggregation choices mandatory. |
| [DistServe paper, OSDI 2024](https://www.usenix.org/system/files/osdi24-zhong-yinmin.pdf) | Primary research motivating separate prefill/TTFT and decode/TPOT constraints and SLO-qualified goodput. Its reported gains are system- and workload-specific and are not claims for this project. |
| [CUDA event API](https://docs.nvidia.com/cuda/cuda-runtime-api/group__CUDART__EVENT.html) | Official CUDA timing/synchronization primitives. Device events are eligible for declared CUDA-device intervals only; host end-to-end timing remains separate. |
| [NVIDIA NVML device queries](https://docs.nvidia.com/deploy/nvml-api/group__nvmlDeviceQueries.html) | Official total-energy counter semantics and explicit `NOT_SUPPORTED` outcome. NVML energy is NVIDIA-device scoped, is not whole-system energy and is unavailable without compatible hardware/driver support. |

## Candidate runtimes and platform seams

| Source | Supported planning use and limit |
| --- | --- |
| [llama.cpp](https://github.com/ggml-org/llama.cpp) | Official candidate local inference project whose documented backends include CPU, Apple Metal and NVIDIA CUDA. A capability listing is not a Lean Model Lab integration or performance result. |
| [Apple: accelerated PyTorch training on Mac](https://developer.apple.com/metal/pytorch/) | Official description of PyTorch's MPS backend and current platform requirements. MPS availability and operator correctness must be probed on the exact host/runtime. |
| [PyTorch profiler](https://docs.pytorch.org/docs/stable/profiler.html) | Official profiling API entry point for CPU and supported device activities. A profiler trace may perturb execution and is diagnostic evidence, not automatically a benchmark result. |
| [PyTorch profiler recipe](https://docs.pytorch.org/tutorials/recipes/recipes/profiler_recipe.html) | Official example of scheduled wait/warmup/active profiling and CPU/CUDA/XPU activities. Exact current backend coverage must be checked at adoption. |
| [vLLM installation and platform documentation](https://docs.vllm.ai/en/stable/getting_started/installation/) | Official capability boundary for a possible later high-throughput serving adapter. Its platform and dependency requirements make adoption conditional on an approved compatible environment. |

## Isolation boundary

| Source | Supported planning use and limit |
| --- | --- |
| [Open Container Initiative runtime specification](https://github.com/opencontainers/runtime-spec/blob/main/config-linux.md) | Primary container contract for namespaces, cgroups/resources, capabilities, filesystem isolation and read-only paths on Linux. It supplies enforcement primitives, not proof that a particular profile is complete or active. |
| [NIST SP 800-190: Application Container Security Guide](https://csrc.nist.gov/pubs/sp/800/190/final) | Authoritative risk guidance for container isolation and security controls. A container is one possible boundary; candidate threat analysis may require a stronger VM or platform sandbox. |

## Research foundations

| Source | Supported planning use and limit |
| --- | --- |
| Hoffmann et al., [Training Compute-Optimal Large Language Models](https://arxiv.org/abs/2203.15556) (NeurIPS 2022) | Primary empirical evidence that model size, training tokens, compute budget and quality interact. Its fitted relationships and model family conditions are hypotheses/reference classes, not a universal recipe for small local experiments or new architectures. |
| Williams, Waterman and Patterson, [Roofline: An Insightful Visual Performance Model for Multicore Architectures](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2008/Archive/EECS-2008-134.pdf) | Primary source for relating operational intensity, bandwidth and peak compute as an analytical ceiling. A roofline model must be calibrated and cannot replace measured application performance. |
| MLCommons, [Algorithmic Efficiency benchmark](https://github.com/mlcommons/algorithmic-efficiency) | Primary/open benchmark programme for time-to-result at target performance across workloads. It informs separate workload, target and repeated-study contracts; this project does not inherit its score or validation. |

## Before adopting a dependency, model or dataset

Record the exact official release/source revision and license; maintenance/advisory state; runtime and transitive dependencies; safe-loading behavior; remote-code, telemetry and network behavior; storage/compute cost; platform constraints; alternatives; and rollback/removal path. A source listed here does not authorize installation, data/model download, cloud use or spend. Exact versions remain a Wave 1 decision because the observed planning host uses arm64 macOS and Python 3.14, while candidate backends have their own compatibility matrices.

For each model and dataset, record provenance, permitted use, attribution, redistribution, access conditions, transformations, partitions, contamination/deduplication analysis, coverage and limitations. Pin tokenizer assets and prompt templates separately from weights. Public availability does not imply compatible rights. Reject incompatible or ambiguous terms and use an honestly labeled synthetic fixture for the contract harness.

## Evidence limits

Official documentation establishes what an upstream project says it supports. A local capability probe establishes what one exact environment exposes. Correctness tests establish a bounded behavior. Controlled repeated measurements establish performance within their workload/hardware/runtime envelope. None alone proves portability, scientific novelty or a production service.

The repository's original content is AGPL-3.0-only. Referenced papers, software, model weights, tokenizers and datasets retain their own terms and are not relicensed by this repository.
