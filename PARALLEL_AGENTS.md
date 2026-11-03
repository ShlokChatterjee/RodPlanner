# Running parallel agents on rodplanner

How to run several Claude Code sessions at once without them clashing, and which checkpoints to split.

## 1. The core idea: one git worktree per agent

A git worktree is an extra working folder attached to the same repo, with its own branch. Each agent works in its own folder, so two agents can never overwrite each other's files while working.

```bash
# from the repo root
git worktree add ../rodplanner-placement -b feature/placement
git worktree add ../rodplanner-vision -b feature/vision
git worktree add ../rodplanner-viewer -b feature/viewer

# then one terminal per agent
cd ../rodplanner-placement && claude
cd ../rodplanner-vision && claude
cd ../rodplanner-viewer && claude
```

Each terminal is an independent session with its own context, files and branch. Recent Claude Code versions also have a built-in worktree option (`claude --worktree <name>`); check `claude --help` for the exact flag.

Worktrees stop file-level clobbering. They do not stop two agents from making incompatible changes to the same function or interface. That only shows up at merge time, so the process below is needed.

Clean up when a branch is merged:

```bash
git worktree remove ../rodplanner-placement
git branch -d feature/placement
```

## 2. The process: planner, feature agents, gated merge

1. **Planner first.** One session writes the task breakdown, the shared interfaces and the file ownership before any feature agent starts. Most conflicts come from agents inventing incompatible interfaces.
2. **Feature agents** each work in their own worktree, on their own branch, only in the files they own. If an agent needs to change a file it does not own, it stops and asks.
3. **Automated gate.** Tests (`pytest`), lint (`ruff`) and type checks run on every branch (CI or a git hook). Machines catch what machines can.
4. **Supervisor reviews and merges.** A separate session reviews what the machines cannot catch: design drift, duplicated code, mismatched assumptions.
   - `git diff main...feature/placement` and the same for the other branches
   - Check for overlapping files and shared interfaces
   - Try a test merge: `git merge --no-commit --no-ff feature/x`, then run the tests
5. **Merge one branch at a time.** Merge A, rebase B onto the new `main`, rerun tests, merge B. The second merge is where most clashes appear.
6. Run `git config rerere.enabled true` so git remembers how a conflict was resolved and does not ask again.

Only the supervisor merges to `main`. Feature agents open PRs and stop.

## 3. Which checkpoints to split

Checkpoints from the project brief:

0. Project setup + design decisions
1. Geometry core (polygons, coverage)
2. Placement algorithm
3. Vision pipeline
4. API layer
5. 3D viewer
6. Benchmarks + validation

### Checkpoint 1: one agent, plus one optional helper

Checkpoint 1 defines the vocabulary everything else depends on: what a roof polygon is, what a rod is, how coverage is computed, units and coordinates. Splitting it early is how agents end up with incompatible assumptions. It is also the checkpoint where learning from one agent building things in order is most valuable.

One piece can safely run in parallel: a **synthetic plan generator**, a script that draws test plans (rectangles, L-shapes, U-shapes) as PNGs and saves the ground-truth polygon beside each. It does not depend on the geometry code, and checkpoints 3 and 6 both need it.

| Agent | Work |
|---|---|
| A | Geometry core: polygon helpers, grid sampling, cone coverage, tests, ADRs |
| B | Synthetic plan generator (small, about an hour) |

### Checkpoints 2, 3 and 5: the best parallel window

After checkpoint 1 fixes the data contract, these three talk to each other only through it.

| Agent | Checkpoint | Input -> Output |
|---|---|---|
| 1 | 2: Placement | polygon + cone parameters -> list of rod positions |
| 2 | 3: Vision | plan image -> polygon |
| 3 | 5: 3D viewer | JSON (polygon, height, rods) -> Three.js scene, built against a hand-written sample JSON |

Checkpoint 4 (API) needs the outputs of 2 and 3, so it waits. Checkpoint 6 waits for everything. Keep checkpoints 0, 4 and 6 on a single agent.

## 4. The contract (write it at the end of checkpoint 1)

Put it in `docs/contract.md` and as typed models in `src/`. This is what lets the three agents run without clashing.

- Polygon format: list of `(x, y)` in metres, closed ring, stated origin and axis direction
- Rod format: `x, y, height`, plus the protection-cone radius rule
- Final JSON schema the viewer reads
- Function signatures, for example:
  - `place_rods(polygon, params) -> list[Rod]`
  - `extract_footprint(image) -> Polygon`

## 5. Conflict points and fixes

| Conflict point | Fix |
|---|---|
| `LEARNING_LOG.md` is shared | Each agent writes its recap to `docs/recaps/cpN.md`; the supervisor merges them into the log |
| ADR numbers collide | Reserve ranges, e.g. 0010-0019 placement, 0020-0029 vision, 0030-0039 viewer |
| `pyproject.toml` / dependencies | Only the supervisor changes dependencies; agents ask first |
| Same files edited | Ownership: placement owns `src/rodplanner/placement/`, vision owns `src/rodplanner/vision/`, viewer owns `viewer/`; nobody edits `geometry/` without asking |
| Second merge breaks | Rebase onto `main` after each merge and rerun tests before merging the next |

## 6. Keeping the learning rule intact

The rule is: full recap at each checkpoint, then back-and-forth questions until satisfied, and nothing moves on before that.

With parallel agents, the agents run in parallel but **your review stays sequential**:

- Review the recaps one at a time (2, then 3, then 5).
- Do not merge a branch until its Q&A is finished.
- If three at once is too much, run only checkpoints 2 and 3 in parallel and do the viewer afterwards.
- Keep the core algorithm in a single session so you can follow it closely.

## 7. Limits to expect

- Parallel agents help most when tasks are genuinely independent. If features share a lot of code, running them one after another is often faster than resolving conflicts.
- Two or three agents is a practical ceiling, because the review work lands on you and the supervisor.
- Give each agent a small, clear task and a definition of done (for example "tests pass and PR is open") so it does not wander into another agent's area.

## 8. Starting prompts (templates)

**Feature agent**

```
You are working on checkpoint N of rodplanner in this worktree/branch only.
Read docs/contract.md first. You own: <folders>. Do not edit anything else;
if you need a change elsewhere, stop and ask me.
Follow the project rules: small steps, tests alongside, type hints, ruff,
clear commits, short ADRs (numbers <range>).
When done: tests green, PR opened, recap written to docs/recaps/cpN.md.
Do not merge.
```

**Supervisor**

```
You review and merge branches for rodplanner. For each feature branch:
diff against main, check for overlapping files and interface mismatches,
do a test merge, run pytest/ruff/type checks, and report problems.
Merge one branch at a time, rebase the next, re-test.
Merge recaps into LEARNING_LOG.md. Only you change dependencies.
```
