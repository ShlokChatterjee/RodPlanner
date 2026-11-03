# Project context: rodplanner

## Who I am
A second-year university student (Computer Science + Mathematics) with no industry
experience. I'm building this to land an internship at a company that does computer
vision and 3D modelling. I want to learn how real teams build software, not just get
working code.

## What we're building
A tool that takes a building plan image (floor plan or roof plan) and automatically
shows where lightning rods should be installed. The company I'm targeting does this
commercially: a task that took people hours is done in about 60 seconds. My version is
a simpler take on the same concept.

Pipeline:
1. Input: plan image (PNG/JPG)
2. Vision: detect the building footprint/walls and convert to a clean polygon
3. Geometry: extrude into a 3D building (user-set height, flat roof first)
4. Placement: compute rod positions so the whole roof is covered
5. Output: 2D overlay with rod positions, 3D viewer showing coverage, JSON/PDF export

## Technical decisions so far
- Language: Python (backend), JavaScript (viewer)
- Libraries: OpenCV (image processing), Shapely (polygon/coverage math), NumPy
- API: FastAPI. 3D viewer: Three.js
- Placement v1: protection-cone coverage model. Sample the roof as a grid of points,
  then use greedy set cover (repeatedly place the rod covering the most uncovered
  points), with a bias toward corners and edges since they are most exposed.
- Placement stretch goal: rolling-sphere method (the basis of IEC 62305, sphere radii
  of 20, 30, 45 or 60 m depending on protection level)
- Vision: start with classical OpenCV (thresholding, morphology, contours) on clean
  plans; upgrade to a segmentation model trained on the CubiCasa5K floor plan dataset
  for messy real-world plans
- Geometry is deliberately separated from the CV code so each can be tested alone

## Scope and honesty
- v1: flat roofs, single building footprint
- Not a certified design tool and does not replace code-compliance review. The README
  must say so.

## Build plan (about 3-4 weeks)
- Week 1: synthetic plans in, polygon out, cone placement, 2D overlay (first working demo)
- Week 2: real, messy plans (the CV part) and the FastAPI endpoint
- Week 3: Three.js viewer with extruded building, rods and coverage domes
- Week 4: polish, timing benchmarks, README with screenshots, 60-second demo video

## How I want you to work with me (important)
This is a learning project. Work like a small real-world engineering team:
- Build in small, reviewable steps. One change at a time, with tests written alongside.
- Use real practices: src layout, type hints, pytest, ruff, git commits with clear
  messages,creating feature branches and short ADRs (architecture decision records) in docs/adr/ for each major
  choice.
- For every significant decision, compare it against the alternatives and explain why
  the chosen option is better for this project. Name the trade-offs, not just the winner.
- Stop at each checkpoint and give me a full recap: what we built, why, what we
  rejected, and the vocabulary I should know. Then answer my questions back and forth
  until I say I'm satisfied. Don't move on before that.
- Save every checkpoint recap in LEARNING_LOG.md.
- Explain things for someone who hasn't worked in industry. Define jargon the first time.

## Checkpoints
0. Project setup + design decisions (repo layout, ADRs, tooling, tests-first habit)
1. Geometry core (polygons, coverage)
2. Placement algorithm (greedy set cover vs alternatives)
3. Vision pipeline (classical OpenCV vs a segmentation model)
4. API layer (FastAPI, validation, error handling)
5. 3D viewer (Three.js)
6. Benchmarks + validation against hand-placed layouts

## What will make this stand out to the company
- A visible timer in the demo ("manual: ~2 hours, this: 8 seconds")
- Validation: compare output to hand-placed layouts on 5-10 plans, report coverage %
  and rod count
- A "what this doesn't do" section in the README
- A stated niche (e.g. residential roofs or warehouse flat roofs)