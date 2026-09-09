# Original quality confirmation queue provenance

This supplement corrects an omission in the reviewed candidate03 research ZIP. The original package inventory named these files and their hashes, but the ZIP did not contain their bytes. The retained original candidate and its inventory are unchanged. This revision adds exact existing bytes; only the product log’s publication extension changes from `.log` to `.txt`.

Read the [queue receipt](receipt.json), [registration](registration.json), [product log](product.txt) and [validation/mapping](supplement-validation.json). Subtract `started_ns` from `execution_started_ns` for waiting (90.012337226 seconds), and `execution_started_ns` from `finished_ns` for archive-process execution (2774.945479864 seconds). Total queue-plus-process wall is 2864.957817090 seconds. The registration and completed receipt share the original start, deadline and exact producer. No clock was restarted and no model run was repeated.

These values exactly match the [activity-cost receipt](../activity-cost-receipt.json). They overlap native-attempt and original-allocation scopes and must not be added to them. Successful process exit alone does not establish quality or efficiency. The separate reviewer checks this correction alongside its immutable candidate03 observations.

The [exact candidate03 manuscript](../manuscript-before-queue-supplement.md) is also preserved. The current manuscript adds only a packaging-correction addendum; its scientific text remains an exact byte prefix. The original package inventory describes that retained pre-supplement state; the new ZIP file manifest inventories the revised distribution.
