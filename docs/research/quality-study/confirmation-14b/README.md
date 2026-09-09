# Current quality investigation: retained benchmark and held-out confirmation

This is **one combined quality investigation**, with one primary [manuscript](manuscript.md). The retained main benchmark, adverse 0.5B history and new held-out control are evidence within that finding, not separately counted findings.

**Result:** median service throughput **4.123×**, median full-attempt efficiency **3.912×**, with **0/256 jointly SLO-qualified responses in each arm**. Every arm scored **127/128**; one question was wrong in every arm. The 128 unique questions were repeated across four arms, producing 512 observations. The frozen quality/parity/practical-effect/relative-tail gates passed; no interactive-serving SLO claim follows.

Read [the revised manuscript](manuscript.md), [prospective methodology](methodology.md), [protocol](protocol.json), [freeze](freeze.json) and [gate result](publication/confirmation-gate.json). The completed original benchmark package and the stopped 0.5B branch remain unchanged one directory above.

Use [the portable entrypoint](portable_reanalysis.py) and [manifest instructions](PORTABLE-REANALYSIS.md) for public reanalysis. Paths are supplied by the manifest, and output must be new. The [five-export validation](portable-validation.json) covers actual derivatives from an unrelated working directory; it is local consistency verification, not independent native or human reproduction.

The publication revision contains [all requests](publication/requests.csv), [attempts](publication/attempts.csv), [pairs](publication/pairs.csv), [token differences](publication/output-differences.csv), [configs and accounting](publication/summary.json), [cost ledgers](publication/cost-ledger.csv), [producer clock views](publication/cost-context.json), [full-prompt split audit](publication/split-audit.json) and [source inventory](publication/source-inventory.json).

Final standalone figures are in `publication/figures/` as PNG, SVG and PDF. Their [source bindings](publication/figure-source-manifest.json), [visual-review receipt](visual-review.json) and [root-relative asset manifest](root-asset-manifest.json) identify exact artifacts for integration. Separate skeptical reproduction, external human review and publication remain pending.

The immutable parent snapshot had analysis clock cutoff `287042909619068` (19,774.044 seconds into the original allocation). Its main 14B native cutoff was `285838453027090`, and its stopped 0.5B development cutoff was `286705871005041`. Those files remain historical evidence. The current combined manuscript includes the distinct held-out native cutoff `291210012268005` and the separately reported later analysis activity.
