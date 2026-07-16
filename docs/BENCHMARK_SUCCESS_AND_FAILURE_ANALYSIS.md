# Benchmark Success and Failure Analysis

Date: July 16, 2026

## Goal

This note converts the current Latto-latto controller results into benchmark-oriented conclusions using:
- explicit success criteria,
- a controller comparison based on those criteria,
- and a failure taxonomy.

This is intended to support paper writing more directly than raw metric tables alone.

## Primary Benchmark Reading

The benchmark should be read primarily through two separate metrics:

- `Streak`:
  how well the controller sustains the alternating-impact rhythm
- `Max |z|`:
  how well the controller regulates vertical drift

These metrics should remain separate in the main benchmark claim because they expose an important tradeoff:
- some controllers are rhythmically successful but poorly regulated,
- others are well regulated but fail rhythmically.

## Secondary Thresholded Success Criteria

### Success@5

Primary benchmark success:

```text
Success@5 = 1 if longest_alternating_streak >= 5
Success@5 = 0 otherwise
```

Reason:
- It rules out accidental alternating collisions.
- It is still achievable enough to separate weak, partial, and strong methods.

### Success@10

Stricter benchmark success:

```text
Success@10 = 1 if longest_alternating_streak >= 10
Success@10 = 0 otherwise
```

Reason:
- It captures more persistent rhythmic competence.
- It is useful as a stronger claim of sustained success.

## Why These Criteria Are Useful but Secondary

- `reward_sum` depends on reward shaping details.
- `Alt.` and `Streak` are more directly connected to the intended behavior.
- `Success@5` and `Success@10` give thresholded, interpretable outcome metrics in the style of benchmark papers such as Meta-World.
- However, they should not replace the primary two-axis reading using `Streak` and `Max |z|`.

## Summary of What the Current Results Say

### Strongest benchmark performer so far

`A2C` is the strongest controller family currently tested.

In particular:
- with `5` seeds, `A2C + z_penalty` is the clearest overall performer across the restitution sweep,
- while `A2C + swing_growth` remains strongest at restitution `e = 0.95` within the swing-growth setting.

### Most stable but weak performer

`PPO` is comparatively stable in `z`, and with `5` seeds it shows more partial rhythmic bursts under `swing_growth`, but it still rarely produces sustained rhythmic success.

### Non-learning baselines

The following controller families currently fail across the tested settings:
- `sinusoidal`
- `random`
- `pumping`

This is useful because it shows the benchmark does not collapse into trivial periodic forcing or blind exploration.

## Failure Taxonomy

The current experiments reveal at least four recurring and interpretable failure modes.

| Failure mode | Metric signature | Typical examples | Interpretation |
| --- | --- | --- | --- |
| Near-stationary collapse | `Alt. = 0`, `Streak = 0`, small `Max |z|` | `PPO + z_penalty`; `PPO + swing_growth` at lower restitution | The controller is stable, but it never builds enough oscillatory energy to achieve sustained alternating impacts. |
| Drift-dominated behavior | positive `Alt.` or `Streak` possible, but moderate to very large `Max |z|` | several `A2C` runs under `z_penalty` and `swing_growth` | Rhythmic behavior appears, but vertical regulation is weak, so the behavior is not physically well controlled. |
| Transient rhythmic burst | positive `Alt.`, moderate `Streak`, often `Success@5` without `Success@10` | `PPO + swing_growth` at high restitution; weaker `A2C` seeds at intermediate restitution | The controller can discover the alternating-impact rhythm, but it cannot sustain it throughout the rollout. |
| High-energy blow-up | very large `Max |z|`, highly variable outcomes across seeds, unstable reward behavior | phase-pumping heuristic; unstable `A2C` seeds with large drift spikes | The controller injects energy too aggressively, producing large excursions and unstable regulation instead of robust rhythmic control. |

This table should be read as an empirical taxonomy for the current benchmark study, not as a proof that the full failure space is closed.

## What This Adds to the Novelty Claim

These benchmark-style results strengthen the paper's novelty in three ways:

1. The benchmark distinguishes controller families clearly.
2. The benchmark exposes multiple interpretable failure modes.
3. The benchmark separates stability from rhythmic success.

That third point is especially important:
- some methods remain stable but never succeed rhythmically,
- some methods achieve rhythmic success but with poor regulation,
- simple heuristics fail entirely.

This is exactly the kind of structural separation that makes a benchmark valuable.

## Recommended Main Claim After Current Results

The current evidence supports the following benchmark claim:

`The Latto-latto benchmark exposes a nontrivial gap between stability-oriented control and sustained rhythmic hybrid-impact success, and it differentiates controller families through both success thresholds and interpretable failure modes.`

## Recommended Next Analysis Step

The next most useful paper-oriented step is:

- generate representative trajectories for each failure mode

Suggested representatives:
- near-stationary PPO rollout
- successful but drift-heavy A2C rollout
- failed sinusoidal or pumping rollout
- transient-burst PPO swing-growth rollout
- high-energy blow-up phase-pumping rollout
