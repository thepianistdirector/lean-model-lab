# Cost scopes for the v1 delivery

The original allocation began at monotonic nanosecond `267268865220540` and ends at `310468865220540`: 43,200 seconds, with at most twelve compute threads, one heavy job, 60 decimal GB RAM and 200 decimal GB project disk. Publication preparation and review share this clock. A new study directory, package, day or reviewer does not restart it.

| Recorded scope | Archive-process execution | What the number covers |
| --- | ---: | --- |
| Fresh 14B quality confirmation | 2,774.945480 seconds | The 512-observation confirmation cell only. Earlier quality development, retained main comparison and adverse legacy work have separate retained costs. The original queue wait is 90.012337 seconds. |
| Complete candidate investigation | 4,104.999706 seconds | Eight studies and 1,984 observations, including both closed feasibility branches, fit/calibration, matched-record control and three confirmation policies. Its separately recorded queue wait totals 5,985.136431 seconds. |
| Complete systems investigation | 3,432.123 seconds | Five studies and 1,600 observations. Its separately recorded queue wait totals 3,420.068 seconds. |

The [quality queue supplement](../research/quality-study/confirmation-14b/queue-provenance/README.md), [candidate cost summary](../research/candidate-study/publication/tables/final/memory-and-timing-summary.json) and [systems budget record](../research/systems-study/provenance/final-campaign-status.json) provide the exact inputs and definitions. Each manuscript retains its original measurement cutoff. The separate reproduction has its own process-cost record and includes the failed, zero-inference candidate admission before the explicitly authorized continuation.

These are overlapping accounting scopes. Attempt wall lies inside archive-process execution; execution and queue waiting lie inside the common allocation span. Historical setup and predecessor records are shared between studies. Adding their reported totals would count some work repeatedly. Lower service time also does not establish lower full-allocation cost, especially when outputs or task quality differ.

The external delivery asset `FINAL-RESOURCE-ACCOUNTING.json` records the later local preparation cutoff, charges every intervening wall second, and reconciles the union of distributed setup/attempt intervals and selected review/build envelopes. Time outside that attributed union remains charged and explicitly unattributed; it is not measured idle time. The record includes its source hashes, original limits and an independent endpoint reconciliation of the interval union. It is accompanied by the exact recording script. The source ZIP and manuscripts remain unchanged by this later accounting snapshot.

A final logical-file disk snapshot is distinct from peak disk use or physical allocated blocks. Attempt-specific server memory high-water marks and sampled aggregate RSS remain in the raw evidence; neither is a continuous allocation-wide peak. Complete CPU utilization, allocation-wide peak telemetry, monetary charges, energy and thermal measurements are unavailable. No values are inferred from processor specifications, and no whole-mission saving is claimed.
