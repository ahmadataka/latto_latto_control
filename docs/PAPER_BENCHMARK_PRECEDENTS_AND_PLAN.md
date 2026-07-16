# Benchmark Paper Precedents and Updated Experiment Plan

Date: July 16, 2026

## Purpose

This note summarizes how relevant reinforcement learning benchmark papers are typically structured, how they design experiments, and what those patterns imply for a Latto-latto benchmark paper.

The goal is not to imitate any one paper exactly, but to extract the recurring structure that makes benchmark papers convincing and publishable.

## Benchmark-Paper Pattern in the Literature

Across the most relevant papers, the structure is surprisingly consistent:

1. Motivate a gap in current RL evaluation.
2. Define a benchmark or environment family that exposes that gap.
3. Explain environment/task design choices clearly.
4. Standardize evaluation protocol and metrics.
5. Run several baseline methods.
6. Show both successes and failure modes.
7. Argue why the benchmark is useful for future algorithm development.

For a Latto-latto paper, this is good news. Our current direction already fits this pattern well.

## What the Relevant Papers Usually Do

### DeepMind Control Suite

Reference:
- Tassa et al., 2018
- https://arxiv.org/abs/1801.00690

What they do structurally:
- Introduce the need for standardized continuous-control benchmarks.
- Explain benchmark structure and design decisions.
- Describe task families and reward conventions.
- Document APIs and implementation details.
- Present benchmark results with multiple RL algorithms.

What matters for us:
- They explicitly discuss task verification: stability of physics and solvability by at least one learning agent.
- They standardize rewards and make evaluation numerically interpretable.
- They use fixed-length evaluation to make results comparable across tasks.

Takeaway for Latto-latto:
- We should explicitly document:
  - why the system is physically stable,
  - why the task is solvable in principle,
  - how evaluation length and metrics are standardized.

### Meta-World

Reference:
- Yu et al., 2019
- https://arxiv.org/abs/1910.10897

What they do structurally:
- Motivate why existing benchmarks are too narrow.
- Define a benchmark with clear task families.
- Introduce an explicit evaluation protocol with different difficulty levels.
- Use a success metric rather than raw reward alone.
- Benchmark several algorithms and analyze what fails.

What matters for us:
- They separate benchmark definition from evaluation protocol.
- They define interpretable success metrics because reward alone is not enough.
- Their experiments first verify that individual tasks are solvable, then test broader benchmark claims.

Takeaway for Latto-latto:
- We should define a clear success criterion beyond reward.
- We should explicitly separate:
  - environment definition,
  - reward definition,
  - evaluation protocol,
  - benchmark claims.

### realworldrl-suite

Reference:
- Dulac-Arnold et al., 2020
- https://arxiv.org/abs/2003.11881

What they do structurally:
- Identify real-world RL challenges one by one.
- Instantiate those challenges in environments.
- Evaluate how standard algorithms degrade as the challenges are increased.
- Combine the challenges into benchmark tasks.

What matters for us:
- They frame the benchmark around the difficulties it isolates.
- They use difficulty levels rather than a single binary task setting.
- They highlight weak points of algorithms instead of only reporting best-case performance.

Takeaway for Latto-latto:
- Our restitution sweep is exactly the right kind of benchmark axis.
- We should lean into the argument that Latto-latto isolates:
  - hybrid impacts,
  - rhythmic control,
  - dissipation,
  - sparse event-based reward,
  - drift-vs-success tradeoffs.

### Benchmarking Reinforcement Learning Algorithms on Real-World Robots

Reference:
- Mahmood et al., 2018
- https://arxiv.org/abs/1809.07731

What they do structurally:
- Introduce benchmark tasks.
- Compare several off-the-shelf algorithms.
- Examine sensitivity and transferability of hyperparameters.
- Focus on reproducibility and readiness for applications.

What matters for us:
- They show that the benchmark contribution can be mostly evaluative.
- They do not need a new algorithm to make a meaningful paper.

Takeaway for Latto-latto:
- We do not need to solve the task perfectly to have a publishable result.
- It is acceptable, and even valuable, if the paper shows that algorithms are unstable or sensitive.

### ContainerGym

Reference:
- Pendyala et al., 2023
- https://arxiv.org/abs/2307.02991

What they do structurally:
- Introduce a benchmark derived from a particular real-world problem class.
- Define how task difficulty can vary.
- Compare standard baselines.
- Use statistical interpretation beyond just reward curves.

Takeaway for Latto-latto:
- A benchmark can absolutely be domain-specific.
- The key is to show that the system exposes a meaningful challenge class, not that it is universally representative.

### RL2Grid

Reference:
- Marchesini et al., 2025
- https://arxiv.org/abs/2503.23101

What they do structurally:
- Standardize tasks, state/action interfaces, rewards, and evaluation.
- Incorporate constraints and domain knowledge.
- Provide baseline results and emphasize what remains hard.

Takeaway for Latto-latto:
- We should present the benchmark not just as a system, but as:
  - a task definition,
  - a metrics package,
  - a set of standard controller baselines,
  - a reproducible evaluation protocol.

### FluidGym

Reference:
- Becktepe et al., 2026
- https://arxiv.org/abs/2601.15015

What they do structurally:
- Argue that progress is hard to assess because prior studies are heterogeneous.
- Introduce a unified benchmark suite.
- Provide baseline results with common RL methods.

Takeaway for Latto-latto:
- This is a strong precedent for our motivation that a small but standardized hybrid-impact benchmark is useful even if many related phenomena can be simulated elsewhere.

### When Cyber-Physical Systems Meet AI

Reference:
- Song et al., 2021
- https://arxiv.org/abs/2111.04324

What they do structurally:
- Build a benchmark.
- Train AI controllers.
- Compare against traditional alternatives.
- Use the comparison to identify limitations and future directions.

Takeaway for Latto-latto:
- This is a strong precedent for comparing RL controllers against heuristic or non-RL controllers, not just against one another.

## Common Experimental Moves in These Papers

Across the papers above, the most common and convincing experiment patterns are:

1. **Environment/task verification**
   - show the task is not broken
   - show it is solvable in principle

2. **Difficulty scaling**
   - vary challenge knobs systematically
   - show performance degrades in an interpretable way

3. **Multiple baseline families**
   - compare more than one RL algorithm
   - ideally include a non-RL baseline or heuristic

4. **Task-specific success metrics**
   - do not rely on reward alone
   - define interpretable success/failure criteria

5. **Failure-mode analysis**
   - analyze characteristic collapses, not only average scores

6. **Reproducibility and statistical care**
   - multi-seed runs
   - standardized rollout length
   - consistent reporting format

## What This Means for the Latto-Latto Paper

The novelty of the Latto-latto paper should be framed as:

- a minimal hybrid-impact benchmark for RL and control evaluation,
- a benchmark that separates stability from rhythmic success,
- a benchmark with a physically meaningful difficulty knob through restitution,
- a benchmark where standard methods reveal informative failure modes.

This is stronger and more defensible than trying to claim a brand-new control algorithm contribution.

## Updated Experiment Plan

Below is the updated plan after comparing our work against benchmark-paper precedents.

### Phase 1: Finalize Benchmark Definition

Needed:
- concise benchmark problem statement
- state, action, dynamics, collision law
- explicit reward definitions
- evaluation protocol

Status:
- mostly done in code and notes

Still needed:
- paper-ready write-up in one place

### Phase 2: Benchmark Verification

Needed:
- show the task is meaningful and not trivial

Recommended experiments:
- zero controller
- random controller
- sinusoidal controller
- one tuned heuristic pumping controller
- uncontrolled rollouts or zero-action rollouts for qualitative reference

Why:
- benchmark papers usually show that the system is nontrivial but not arbitrary

### Phase 3: Core Controller Benchmark

Needed controller families:
- PPO
- A2C
- SAC
- sinusoidal heuristic
- random baseline
- one simple energy-pumping heuristic if possible

Why:
- This gives algorithm diversity plus non-RL comparison.

Current status:
- PPO done
- A2C done
- sinusoidal done

Still needed:
- SAC
- random
- heuristic pumping controller

### Phase 4: Difficulty Study

Needed:
- systematic difficulty knob with restitution

Recommended settings:
- `e = 1.0`
- `e = 0.95`
- `e = 0.9`
- `e = 0.8`

Why:
- This is our clearest benchmark axis and closest analogue to challenge scaling in benchmark papers like realworldrl-suite.

Status:
- already done for PPO, A2C, sinusoidal

### Phase 5: Reward Study

Minimal reward family set:
- `sparse_only`
- `z_penalty`
- `swing_growth`

Optional:
- `deadzone`

Why:
- This is enough to show that reward design matters materially.

Current status:
- strong early results exist

Still needed:
- a more paper-ready condensed table or figure

### Phase 6: Success Criterion

Needed:
- an interpretable benchmark success criterion

Recommended definition:
- define success if `longest_alternating_streak >= K`
- consider `K = 5` or `K = 10`

Why:
- benchmark papers often use success rates or interpretable thresholds instead of raw reward alone

Deliverables:
- success rate per controller and restitution
- possibly success rate per reward variant

### Phase 7: Failure Taxonomy

Needed:
- categorize failure types observed in rollouts

Recommended categories:
- near-stationary collapse
- drift-dominated behavior
- transient rhythmic burst then loss of rhythm
- unstable high-energy blow-up

Why:
- benchmark papers are stronger when they explain not only what score was achieved, but how the controller failed

### Phase 8: Statistical Strengthening

Needed:
- more seeds for the most important comparisons

Recommendation:
- keep exploratory studies at 3 seeds
- expand the most important cells to 5 or 10 seeds

Priority cells:
- PPO + `z_penalty`
- PPO + `swing_growth`
- A2C + `z_penalty`
- A2C + `swing_growth`

Why:
- This gives stronger claims without exploding compute everywhere.

### Phase 9: Final Benchmark Figures

Needed:
- one main comparison table
- one restitution-vs-performance figure
- one set of representative trajectories
- one failure-mode figure

Recommended main figure content:
- x-axis: restitution
- y-axis: alternating collisions or success rate
- separate curves by controller and reward variant

### Phase 10: Paper Positioning

Needed:
- short, precise claim relative to existing benchmarks

Recommended claim:

`Latto-latto is a minimal hybrid-impact benchmark for reinforcement learning and control evaluation, designed to expose the gap between stability-oriented behavior and sustained rhythmic success under dissipative impacts.`

## Priority Order from Here

If we prioritize strictly for novelty support, the next steps should be:

1. add `SAC`
2. add `random` and a tuned pumping heuristic
3. define benchmark success criterion
4. create failure-mode taxonomy with representative trajectories
5. expand seeds for the most important controller-reward pairs
6. make final paper figures and tables

## Bottom Line

Compared with the benchmark papers above, the Latto-latto project is already on the right track. The main missing pieces are not conceptual anymore. They are:

- stronger baseline coverage,
- clearer success/failure definitions,
- richer failure analysis,
- and a more paper-ready presentation of the benchmark protocol and results.

That is a good position to be in.
