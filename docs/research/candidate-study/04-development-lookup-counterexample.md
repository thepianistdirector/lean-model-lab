# Development lookup counterexample

This is an illustrative case from the complete 32-table fit population, not fresh confirmation. On `r024`, the full model returns the expected value `DRIXT`; the exact dependency slice returns the query key `DDMVJ`. The same outputs recur in both AB/BA repetitions. No transitive reference occurs: the retained context is a single direct VALUE assignment.

The selected record and unchanged query are:

```text
VALUE DDMVJ DRIXT
ASK DDMVJ
```

The certificate reports `dependency_closure_preserved=true`, `input_record_count=24`, `retained_record_count=1`, `closure_record_count=1`, and selected original line indices `[25]` (zero based). Its scope is syntax/dependency closure only and explicitly does not promise model answer equivalence. Independent reanalysis resolves both full and sliced record tables to `DRIXT`. Both native responses finish at EOS; neither hits the token cap.

| Repetition | Expected | Actual full output | Actual slice output | Class |
| --- | --- | --- | --- | --- |
| AB | DRIXT | DRIXT | DDMVJ | Full only correct |
| BA | DRIXT | DRIXT | DDMVJ | Full only correct |

The complete original context is retained below, so the example is reviewable without hiding competing records:

```text
RECORD-LANGUAGE v1
TASK record-lookup
RULES Last assignment wins. REF follows the final assignment of its target.
OUTPUT Resolve ASK to a VALUE. Reply with that alphabetic value only.
BEGIN
VALUE DRRJE DVLIP
VALUE DKDIR DHXCS
VALUE DXPZJ DXJIE
VALUE DFVLX DXHRY
VALUE DSPFH DRWUD
VALUE DTONQ DOUDP
VALUE DYAXR DUALH
VALUE DDVEB DWYXT
VALUE DHNWB DOPLS
VALUE DAZBP DUTCW
VALUE DDMVA DAXIO
VALUE DQOMQ DWHUB
VALUE DYWGQ DNHLM
VALUE DZBEZ DUDGC
VALUE DHBNA DHJCB
VALUE DIBXY DGVDF
VALUE DNLYT DNBAL
VALUE DVZEM DZPGR
VALUE DHYJS DLDQX
VALUE DMBZK DUGPL
VALUE DDMVJ DRIXT
VALUE DNPMH DAMBC
VALUE DNJFT DZMQS
VALUE DWLTA DUGBO
END
ASK DDMVJ
ANSWER:
```

The complete selected prompt is:

```text
RECORD-LANGUAGE v1
TASK record-lookup
RULES Last assignment wins. REF follows the final assignment of its target.
OUTPUT Resolve ASK to a VALUE. Reply with that alphabetic value only.
BEGIN
VALUE DDMVJ DRIXT
END
ASK DDMVJ
ANSWER:
```

The [case artifact](publication/artifacts/counterexamples/development-lookup-r024.json) retains both actual output token sequences, native attempt/trace hashes and full certificates. The [complete paired population table](publication/tables/development-stage1/paired.csv) and [request-level outputs](publication/tables/development-stage1/requests.csv) are shipped with the portable analysis; the corresponding fit study's all-offered classes are 2 both-correct, 2 full-only, 8 slice-only and 20 both-wrong per repetition. This example illustrates one of the two harmful cases, not a selected success subset. Its conditional full/slice oracle ceiling is 12/32 for the entire fit population. Confirmation cases will be reported separately, without treating this development illustration as held-out evidence.

Artifact hashes in the case file identify original producer bytes. Export provenance records any metadata-redacted derivatives; answer text, records, timing values and certificates used here remain unchanged.
