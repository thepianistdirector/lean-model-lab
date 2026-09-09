# Public publication reconciliation

Reobserved 2026-09-08, unauthenticated public reads of all five exact campaign/roadmap/task/proposal URLs. The same zero-task/no-published-plan/revision-1 Discussion state remains. Hash receipts: `../evidence/public-state-20260908.json`. No platform write has occurred.

- [Campaign](https://tanduna.com/projects/lean-model-lab): foundation story, 0 native tasks, 0 releases.
- [Roadmap](https://tanduna.com/projects/lean-model-lab/roadmap): no published task plan.
- [Tasks](https://tanduna.com/p/lean-model-lab/tasks): 0 tasks, no pagination links.
- [Proposals](https://tanduna.com/p/lean-model-lab/proposals): one discussion proposal.
- [Existing proposal](https://tanduna.com/p/lean-model-lab/proposals/prp_b4937892fb5adf25392c481d939656bd): revision 1, Discussion; no accepted decision inferred.
- Live project identity: `prj_9fed8235f17a02a46fb64411f806a2bc`, obtained from the exact workspace page, not guessed from its slug.

## Supported path

The [public MCP reference](https://tanduna.com/docs#mcp) exposes task draft creation, optimistic-revision plan saving, saved-draft submission and published-plan readback. `tanduna.task_plans.save_draft` supports at most 32 waves, wave names up to 80 characters and up to 1000 selected task IDs/dependency entries. Native IDs must be returned by actual calls; canonical IDs are not native IDs.

`submit_draft` freezes an exact saved revision for textual review and requires explicit agreement. Submission does not execute, vote or publish. Publication needs a real passing review and approval of the exact linked poll option. Disabled review remains pending. Historical external completion cannot be represented as runner-reviewed completion without the platform evidence workflow.

No callable authenticated Tanduna tools were found in this task's available tool inventory. [Connection instructions](https://tanduna.com/guide/connect-through-mcp) require the owner to complete sign-in locally on the computer with their browser and then verify the connected tool session. The guide explicitly says not to run its login helper on a different remote machine. No credentials will be requested in chat, copied from another task or added to this project.

Prepare the generated canonical export and source-successor mapping first. Once an authenticated supported session and concrete scope approval are available: freshly read the project/proposal/draft, reconcile any new records, create or revise unpublished drafts idempotently, preserve returned IDs and revisions, save the named plan, submit only the agreed saved revision, and retain actual review/decision evidence. Read back the public campaign, separate published plan, wave order, task count, dependencies, release horizons/status and real 0.1 access instructions. Stop on conflicts and read current state before retrying. Do not fabricate votes or use direct database writes.

## GitHub

An existing GitHub CLI session identifies `thepianistdirector`. Authentication is capability, not destination-specific release approval. Exact branch/diff, tag, release artifacts and public data scope must be reviewable before the final publication decision. No push, release or repository setting change has occurred. Git author configuration is absent; historical author metadata alone is not a configured identity.

## Gates

The local export is not a published roadmap. A draft or pending proposal is not a published plan. A local source archive is not a publicly obtained, externally reproduced product. Keep all those evidence states separate and the native Goal incomplete until its conjunction of requirements is verified.
