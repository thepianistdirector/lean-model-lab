# Offline workbench review — 8 September 2026

Latest v1 addendum: [archive06 actual workbench checks](../evidence/v1-final-workbench-browser.json) now pass keyboard skip/filter/reset/disclosure segments, visible focus, native 200% zoom and 390px narrow reflow. The largest retained 2,048-row study loaded in 496 ms in one check. [Unedited screenshots](../release/screenshots/README.md) are included. The historical assessment below preserves earlier boundaries; these later checks do not establish a human screen-reader observation or accessibility certification.

The first real v1 comparison and recovery artifacts have now been reviewed in an actual browser, with scoped UI fixes and retained screenshots. Keyboard task segments, 375px reflow, request disclosures, missing observations and cost history were exercised. This is **not broad accessibility certification**. A tiny native 200% browser-zoom proof has passed; the actual final v2/14B artifact review remains unfinished and separate.

## Scope and evidence boundaries

`build_catalog(studies: list[Path]) -> dict` opens each source with `Session`, requires complete/reconciled terminal reservation inventory, and evaluates it with `evaluate_inventory`. A finalized inventory can have an incomplete comparison schedule. Such campaigns retain all attempts, expected request rows, missing counts, costs, and ineligibility reasons. Unresolved reservations, torn journal indexes, changed normalized evidence, changed raw inventories, and duplicate source sessions are refused; no source repair occurs. Independent sessions with identical configurations remain separate.

Scientific ratios are confined to within-study comparisons and nulled for globally ineligible campaigns, including otherwise healthy subgroups. Strict compatibility groups include every frozen configuration field except study ID and clock, including model, tokenizer, workload, engine, candidate, sampling, evaluation, hardware, implementation, backend revision, patch, and binary. Group membership does not authorize pooled or cross-study ratios. Fixture labels and measured claim eligibility remain explicit.

Labels use sanitized local basenames; duplicate basenames receive stable study-ID suffixes. The catalog stores no source root path or private-path links. Source references contain bundle-relative document names and JSON pointers. Operational setup descriptions are omitted because they can include local paths; typed cost fields and complete setup history remain. Retained model output text is exact evidence and is escaped rather than rewritten; it can contain arbitrary text.

Native cache evidence is available only for the supported pinned protocol when tokenizer inputs and successful responses reconcile with normalized requests and cache counters. Unavailable evidence remains explicit; arm labels never imply cache counts. Native replay verifies consistency, not authenticity. Failed responses retain their normalized evidence without fabricated native terminal accounting. The workbench loads no model.

## Actual browser review of the first v1 artifacts

The reviewed data contained **1,792 expected request rows and 14 retained attempts** across a comparison study and an interrupted/retried recovery study. The original HTML was preserved; scoped generator fixes were reviewed against regenerated copies of the same data. This observation does not cover a newly generated v2/14B final workbench.

| Task | Actual observation | Limits |
| --- | --- | --- |
| Identify studies and findings | Two identically named `study` inputs now display `study [study-1]` and `study [study-2]`. Long reason text wraps at 375px. | No cross-study inference or ratio is added. |
| Combine seven request filters | Study, workload family, concurrency, pair, arm, request quality and paired token evidence were changed with Tab/arrows/End. One combined selection produced `r108` and `r121`, 2 of 1,792 rows. | Some task segments began with programmatic focus/scroll positioning; a complete keyboard-only traversal from browser launch is not claimed. |
| Open request evidence | Space opened the native disclosure. `r108` showed expected `XTIQG`, observed `river`, IDs `[5469,151645]`, generated count 2, prompt count 75, and reused/new counts 63/12. Paired token/text mismatches and matching prompt counts were readable. | Exact normalized JSON remains available beneath the readable fields. |
| Inspect adverse setup and costs | Native disclosure showed full wall 2,423.214019s, attributed setup/attempts 1,551.313645s, idle/coordinator 871.900374s, retained attempts 1,298.379573s; two failed builds and a failed protocol check remained visible. | These are the reviewed v1 study's retained costs, not current campaign totals. |
| Recover from empty filtering | A contradictory correct-request/token-mismatch selection showed 0 of 1,792 and a visible explanation. Space on reset restored every row and cleared all seven selectors. | All 14 attempts stayed visible while request filters changed. |
| Inspect interruption and retry | Recovery study selection showed 256 expected rows, including 123 missing observations beginning at `r005`; interrupted 5/128 and completed 128/128 attempts both remained visible. | Missing observations were not replaced by fabricated results. |
| Use the narrow layout | At 375×812, page scroll/client widths both equaled 360px; controls were 44px high and within the page. Right Arrow moved the focused request-table scroll region from 0 to 40px while page width stayed fixed. | 320px and 400% reflow remain untested. |
| Inspect accessibility semantics | Browser accessibility tree exposed all seven selector names and a polite/atomic count status. Visible focus was inspected during keyboard segments. | No human screen-reader session was performed. |

The final filter copy/width adjustments were visually checked at desktop, 375px and 200% CSS content enlargement. Earlier captures were inspected for open request details, failed setup/costs and the empty state. The included [v1 workbench evidence summary](../evidence/browser-0.4-v1-workbench.json) records the observed results, artifact/capture hashes and provenance limits. Full HTML, captures and raw receipts remain locally in `.cache/workbench-browser-0.4-first/` and are not distributed in the source archive.

## Browser infrastructure and native zoom gate

Approved AlmaLinux RPMs were acquired with pinned hashes and verified signatures, inspected without script execution, and only needed shared libraries/symlinks/notices were staged inside the project. No package installation, global configuration change, service or public server was used. The v1 browser review used existing Chromium headless shell 140.0.7339.186 over CDP pipes with its sandbox enabled. All four review runs closed with no remaining owned processes or TCP listeners; no page JavaScript exceptions or console errors were recorded. Chromium's GPU-process sandbox-initialization warning is retained in receipts.

The shell's native Ctrl-plus shortcuts did not change zoom. A separate `body.style.zoom='200%'` check passed reflow and label visibility, but **CSS content enlargement is not native browser zoom**. It does not close that gate.

Full Chromium 140 starts after assigning a short, private project-local child `TMPDIR`; the prior SIGTRAP was traced to a 193-byte singleton socket path, above its 107-byte non-NUL limit. The short actual path is 105 bytes. A tiny baseline page reached native `Page.getLayoutMetrics.cssVisualViewport.zoom=1`, DPR 1, unchanged 100px CSS probe width, and sandboxed renderers (`Seccomp=2`, `NoNewPrivs=1`). The original misleading harness failure is retained with an [included adjudication summary](../evidence/browser-0.4-native-zoom.json).

Full Chromium attempted background Google URLs despite its background-networking flag. The root-approved process-local hostname rule subsequently produced seven name-resolution failures; a netlog UDP connect was traced to Chromium's local IPv6 route/address probe, which calls connect/getsockname/close without sending. This is not universal egress isolation and does not mean there were zero attempted requests. The included [native-zoom evidence summary](../evidence/browser-0.4-native-zoom.json) records the network scope and source references; the [pinned Chromium probe implementation](https://chromium.googlesource.com/chromium/src/+/140.0.7339.186/net/dns/host_resolver_manager.cc#1534) identifies the connect/local-address path.

**The tiny native 200% proof now passes.** At the same 1440×1000 outer window, native zoom changed 1 → 2, CSS viewport width 1440 → 720 and DPR 1 → 2, with visual scale 1 and unchanged CSS. Both captures were inspected; both runs closed cleanly and removed their short temporary directories. The reviewed network gate accepted only the exact closed route/address probe, with no unmatched connection/send events. The included [native metrics and evidence hashes](../evidence/browser-0.4-native-zoom.json) identify the retained receipts, harnesses, netlogs and captures. Those raw artifacts remain in local `.cache/browser-review/` and are not distributed in the source archive. The actual final v2/14B HTML must still be opened and checked at native 200% between inference studies. The large workbench remains excluded during active measurement. Infrastructure proof alone does not verify its final layout or content.

## Implementation and automated checks

The interface uses semantic landmarks, headings, table captions/column scopes, labelled native controls and disclosures, visible focus, and at least 44px control height. Counts use a polite live status without moving focus. Tables have labelled keyboard-focusable scrolling regions; status remains textual and does not rely on color alone.

The standalone document has no external resource dependencies, fetch calls or telemetry. This statement applies to workbench code, not every internal activity of the browser hosting it. CSP restricts connections, external resources, form submission and base URL changes. Inline CSS and the local filter script are permitted. HTML evidence is escaped; embedded JSON escapes markup delimiters and Unicode line separators. The filter script uses datasets and `textContent`, not `innerHTML`.

After the final audited generator changes, all **16 workbench tests passed**:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests python -m unittest tests/test_workbench.py -q
```

Coverage includes source preservation, unresolved/tampered evidence, duplicate sessions, compatibility boundaries, incomplete recovery schedules, expected denominators, retry ambiguity, token/text parity, cache consistency, hostile output escaping, labelled controls and semantic tables. Node exercises the embedded filter logic in a controlled DOM harness. Actual browser interaction evidence is recorded separately above. No-script disabled controls and fallback content have static assertions, but browser no-script behavior is not yet verified.

## Remaining scoped checks

1. Repeat the actual final v2/14B workbench's filters, disclosures, counts, cost history and native 200% layout after final artifact handoff, using the now-proven native zoom method. Keep final artifact identity/hashes distinct from this v1 review.
2. Complete keyboard traversal from skip link through all sections, seven selectors, reset and disclosures; check for focus traps across the complete page.
3. Exercise 320px and 400% reflow, human screen-reader labels/table headers/live counts/disclosures, forced colors, measured contrast, print and actual no-script fallback.
4. Profile and assess the largest admitted multi-study catalog. Successful loading of this 1,792-row artifact is not a performance or scalability benchmark.

These limits do not invalidate the observed v1 task results or source-validation tests; they bound browser compatibility and accessibility claims.
