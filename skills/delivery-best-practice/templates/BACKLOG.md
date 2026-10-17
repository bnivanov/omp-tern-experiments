# Backlog

Ids are stable and never reused. Before allocating an id, scan Open and Done. If a candidate collides, generate another unique id before anything references it. Do not change an id after it has been written or cited. Do not delete rows. Archive only with explicit authorization.

If a board owns execution status, put `Selected: <card-id>` and the board/project pointer in Source when work is selected. The card references this stable backlog id; a different task gets a new id. Do not mirror live execution statuses here. Done records historical disposition with pointers to the card and plan/handoff evidence, not copied evidence.

## Open

| Id | Item | Why | Source | Added |
|---|---|---|---|---|

## Done

| Id | Item | Done | Evidence |
|---|---|---|---|
