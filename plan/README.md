# Canonical programme and immutable lineage

`tasks.json` is the task, dependency, release-horizon and evidence-status authority. `STATUS.md` summarizes execution evidence; `TASKS.md`, `ROADMAP.md` and `tanduna-export.json` are exact generated projections. Change the canonical ledger before regenerating views:

```sh
python3 tools/generate_plan.py
python3 tools/generate_plan.py --check
python3 tools/validate_plan.py
python3 tools/validate_plan.py --self-test
```

The accepted source revision contains 27 task objects and 71 structured edges. Byte-identical copies of its plan, roadmap, contributor tasks, status and validator are retained in `lineage/821c6364/`. Fixed SHA-256 values in the validator protect their history independently of mutable ledger metadata. Stale historical entry wording remains historical; the source's three DONE foundation tasks remain accepted documentation/tooling. New task rows cannot convert those three completions into product evidence.

The active programme has 219 outcomes: three retained foundation rows and 216 new outcomes in 29 outcome waves. Forty successors target the narrow CPU 0.1. Later horizons retain training, analytical calibration, hardware measurement, advanced inference, numerical methods, protected confirmation, distributed execution, accessible inspection and portable reproduction. Eight agent-search outcomes are explicitly exploratory proposals, with no committed release promise.

Each original task has an explicit source mapping, exact original acceptance and revision, original structured prerequisites, separately recorded textual-only prerequisites, reason and successors. The source inventory records no additional textual-only prerequisite or frozen predecessor; empty arrays and nulls preserve that observed absence rather than inventing identities. The full source prose remains inspectable. Mapping a bounded inference-only successor does not complete a broader source requirement or delete its training/analytical dependencies.

Each active outcome includes project-scoped key, area, wave, horizon, dependencies with prerequisite-outcome rationale, falsifiable acceptance, source class/references, evidence needs and honest status. Immediate execution adds a bounded packet with an owner, actual files/commands, falsifiers, resource permissions and exit evidence. Future paths are not invented implementation modules. New work starts PLANNED with NOT TESTED evidence; later statuses require evidence records. DONE is reserved for the accepted historical foundation.

`validate_plan.py` rejects duplicate identities/outcomes, missing or malformed mappings, changed source history, missing prerequisite rationale, cycles, dangling/later-wave/later-release edges, orphan tasks or waves, projection drift and unsupported completion/native-ID claims. Its negative controls use disposable fixtures inside this project's `.cache`, and start from the accepted DONE foundation rather than stale READY FOR REVIEW assumptions. These checks validate planning; they establish no scientific result.

The Tanduna export is publication material, not an executable native API payload or evidence of publication. It retains the root's freshly verified project identity and existing DISCUSSION proposal, while task and native-plan IDs remain null until returned by supported operations. Resolve real IDs, use the current documented schema, satisfy authorization/review/poll gates and verify public read-back. Do not replace the required native plan with a source link or mark a draft export complete. The 28 wave names fit the native 32-wave/80-character limits.
