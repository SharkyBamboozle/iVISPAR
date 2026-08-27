# Open questions

The registry of open design and engineering questions, each with a stable
`Q##` ID — never renumbered, **rows never deleted**.

**Lifecycle.** A question enters 🔴 with a summary and pointers to (a) the
topic page holding the analysis and (b) the roadmap spike or epic that will
answer it. When resolved, the row **stays**: status flips to ✅, the summary
gains `**Resolved (Session N):** <one-line outcome>`, and Pointers becomes
`Resolved by [ADR-00NN]` — the resolving ADR reciprocally records "resolves
Q##". Deferred questions go 🧊 with their **reactivation trigger inline**.
Questions may gate other questions or requirements; write that dependency into
the row.

**Status legend:** ✅ Resolved · 🟡 Tentatively answered · 🔴 Open ·
🧊 Deferred.

| ID | Status | Summary | Pointers |
|----|--------|---------|----------|
| Q1 | 🔴 | How are geom-board datasets regenerated? The A* solver module never reached the dev tree; the algorithm survives only in the frozen tag (`Source/Configure/find_shortest_move_sequence.py`). | port task in the packaging wave · gates Spike A |
| Q2 | 🔴 | May the bundled Poliigon textures be redistributed in the public repo? No license file accompanies them; they are already public in the frozen tag. | blocks the Unity wave |
| Q3 | 🔴 | How deep must the pre-cutover reproduction gate be — transport smoke or full scripted episode? | answered by Spike A · operator decision |
| Q4 | 🧊 | HPC/cluster support (Apptainer image, local open-weights models). | Deferred — reactivate as the first post-cutover epic; answers public issue #6. |
