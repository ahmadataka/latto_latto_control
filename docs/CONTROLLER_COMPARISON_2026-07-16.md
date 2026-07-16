# Controller Comparison on Restitution Sweep

Date: July 16, 2026

Setup:
- Seeds: `0, 1, 2`
- Timesteps for RL methods: `500000`
- Reward variants: `z_penalty`, `swing_growth`
- Restitution values: `1.0`, `0.95`, `0.9`, `0.8`

## Reward Definitions

Let:
- `z_t` be the vertical pivot position at time step `t`
- `theta_t` be the pendulum angle at time step `t`
- `z_tol` be the drift dead-zone tolerance
- `alpha` be the vertical drift penalty weight
- `beta` be the swing-growth reward weight
- `w_c` be the alternating-collision reward weight

The alternating-collision event reward is:

```text
r_collision(t) =
  w_c, if a collision occurs at time t and the collision side alternates
  0,   otherwise
```

The drift penalty uses the excess over the dead-zone:

```text
z_excess(t) = max(0, |z_t| - z_tol)
```

```text
r_z_penalty(t) = alpha * z_excess(t)^2
```

The swing amplitude proxy is defined relative to the middle angle:

```text
A_t = |theta_t - pi/2|
```

Only positive amplitude growth is rewarded:

```text
Delta_A_t = A_t - A_(t-1)
```

```text
r_swing_growth(t) = beta * max(0, Delta_A_t)
```

The reward variants used in this comparison are:

### z_penalty

```text
r_t = r_collision(t) - r_z_penalty(t)
```

### swing_growth

```text
r_t = r_collision(t) - r_z_penalty(t) + r_swing_growth(t)
```

Parameter values used in this experiment:
- `w_c = 1.0`
- `alpha = 0.01`
- `z_tol = 0.0`
- `beta = 0.05` for `swing_growth`

Metric legend:
- `Alt.`: mean alternating collisions
- `Streak`: mean longest alternating streak
- `Max |z|`: mean maximum absolute pivot drift

## Benchmark Reading Guide

For benchmark interpretation, the primary view should use two separate axes:

- `Streak`:
  rhythmic success quality
- `Max |z|`:
  regulation quality

These should remain separate in the main paper because they capture different controller properties. A controller may achieve strong rhythmic behavior with poor regulation, or good regulation with no meaningful rhythmic success.

## Secondary Success Criteria

For thresholded reporting, the following success criteria are recommended as secondary summaries:

### Primary success criterion

```text
Success@5 = 1 if longest_alternating_streak >= 5
Success@5 = 0 otherwise
```

Interpretation:
- This is the main benchmark success metric.
- A controller is counted as successful if it can sustain at least five alternating collisions in sequence.
- This threshold is strict enough to rule out accidental or one-off alternating events, but permissive enough to distinguish partially competent methods from total failure.

### Secondary strict success criterion

```text
Success@10 = 1 if longest_alternating_streak >= 10
Success@10 = 0 otherwise
```

Interpretation:
- This is a harder success metric for stronger rhythmic persistence.
- It is useful to distinguish controllers that occasionally find the rhythm from controllers that sustain it more convincingly.

### Why use thresholded success criteria in addition to the two main metrics

- `reward_sum` depends on the reward variant and can mix multiple effects such as drift penalty and swing-growth shaping.
- `Success@5` and `Success@10` are directly tied to the benchmark objective: sustained alternating impacts.
- This matches the practice in many benchmark papers where an interpretable thresholded success metric is reported in addition to reward.
- However, these thresholded criteria should supplement, not replace, the main two-axis reading based on `Streak` and `Max |z|`.

## z_penalty

| Controller | e=1.0 | e=0.95 | e=0.9 | e=0.8 |
| --- | --- | --- | --- | --- |
| PPO | Alt. `0.00`, Streak `0.00`, Max \|z\| `0.048` | Alt. `0.00`, Streak `0.00`, Max \|z\| `0.044` | Alt. `0.00`, Streak `0.00`, Max \|z\| `0.065` | Alt. `0.00`, Streak `0.00`, Max \|z\| `0.131` |
| A2C | Alt. `8.67`, Streak `8.67`, Max \|z\| `6.492` | Alt. `5.00`, Streak `5.00`, Max \|z\| `7.604` | Alt. `5.67`, Streak `5.67`, Max \|z\| `7.338` | Alt. `6.00`, Streak `6.00`, Max \|z\| `1.405` |
| Sinusoidal | Alt. `0.00`, Streak `0.00`, Max \|z\| `1.908` | Alt. `0.00`, Streak `0.00`, Max \|z\| `1.908` | Alt. `0.00`, Streak `0.00`, Max \|z\| `1.908` | Alt. `0.00`, Streak `0.00`, Max \|z\| `1.908` |

## swing_growth

| Controller | e=1.0 | e=0.95 | e=0.9 | e=0.8 |
| --- | --- | --- | --- | --- |
| PPO | Alt. `1.67`, Streak `1.67`, Max \|z\| `0.186` | Alt. `2.00`, Streak `2.00`, Max \|z\| `0.095` | Alt. `0.00`, Streak `0.00`, Max \|z\| `0.064` | Alt. `0.00`, Streak `0.00`, Max \|z\| `0.083` |
| A2C | Alt. `4.33`, Streak `4.33`, Max \|z\| `9.870` | Alt. `10.67`, Streak `10.67`, Max \|z\| `1.065` | Alt. `5.67`, Streak `5.67`, Max \|z\| `2.836` | Alt. `3.67`, Streak `3.67`, Max \|z\| `9.318` |
| Sinusoidal | Alt. `0.00`, Streak `0.00`, Max \|z\| `1.908` | Alt. `0.00`, Streak `0.00`, Max \|z\| `1.908` | Alt. `0.00`, Streak `0.00`, Max \|z\| `1.908` | Alt. `0.00`, Streak `0.00`, Max \|z\| `1.908` |

## Quick Read

- `PPO` is drift-stable but usually fails to generate sustained alternating impacts.
- `A2C` is much more capable of producing alternating impacts, but it is far more volatile and often allows large `z` drift.
- The default `sinusoidal` controller fails across all tested restitutions and reward variants.
- `A2C + swing_growth` is strongest at `e = 0.95`.
- `A2C + z_penalty` is the most persistent performer across the full restitution sweep.

## Paper-Ready Threshold Tables

These tables are useful as secondary summaries, but the main benchmark interpretation should still rely on the separate reporting of `Streak` and `Max |z|`.

### Success@5

| Controller | Reward | e=1.0 | e=0.95 | e=0.9 | e=0.8 |
| --- | --- | --- | --- | --- | --- |
| PPO | `z_penalty` | `0.00` | `0.00` | `0.00` | `0.00` |
| PPO | `swing_growth` | `0.33` | `0.33` | `0.00` | `0.00` |
| A2C | `z_penalty` | `0.67` | `0.33` | `0.67` | `1.00` |
| A2C | `swing_growth` | `0.33` | `1.00` | `0.67` | `0.33` |
| Sinusoidal | `z_penalty` | `0.00` | `0.00` | `0.00` | `0.00` |
| Sinusoidal | `swing_growth` | `0.00` | `0.00` | `0.00` | `0.00` |
| Random | `z_penalty` | `0.00` | `0.00` | `0.00` | `0.00` |
| Random | `swing_growth` | `0.00` | `0.00` | `0.00` | `0.00` |
| Pumping | `z_penalty` | `0.00` | `0.00` | `0.00` | `0.00` |
| Pumping | `swing_growth` | `0.00` | `0.00` | `0.00` | `0.00` |

### Success@10

| Controller | Reward | e=1.0 | e=0.95 | e=0.9 | e=0.8 |
| --- | --- | --- | --- | --- | --- |
| PPO | `z_penalty` | `0.00` | `0.00` | `0.00` | `0.00` |
| PPO | `swing_growth` | `0.00` | `0.00` | `0.00` | `0.00` |
| A2C | `z_penalty` | `0.67` | `0.33` | `0.33` | `0.00` |
| A2C | `swing_growth` | `0.33` | `1.00` | `0.00` | `0.00` |
| Sinusoidal | `z_penalty` | `0.00` | `0.00` | `0.00` | `0.00` |
| Sinusoidal | `swing_growth` | `0.00` | `0.00` | `0.00` | `0.00` |
| Random | `z_penalty` | `0.00` | `0.00` | `0.00` | `0.00` |
| Random | `swing_growth` | `0.00` | `0.00` | `0.00` | `0.00` |
| Pumping | `z_penalty` | `0.00` | `0.00` | `0.00` | `0.00` |
| Pumping | `swing_growth` | `0.00` | `0.00` | `0.00` | `0.00` |

### Reading the success tables

- `PPO` rarely reaches even `Success@5`.
- `A2C` is the only controller family that repeatedly crosses the benchmark success threshold.
- `A2C + swing_growth` is strongest under `e = 0.95` by the strict `Success@10` metric.
- `A2C + z_penalty` is the most persistent controller-reward pair across the full restitution sweep.
- All non-learning baselines currently fail under both success thresholds.

## Additional Baseline Notes

The following additional baselines were tested on Thursday, July 16, 2026:

### random

- Evaluated across `z_penalty` and `swing_growth`, with restitution values `1.0`, `0.95`, `0.9`, and `0.8`.
- Result:
  `Alt. = 0` and `Streak = 0` in every tested setting.
- Interpretation:
  Random exploration alone does not discover the alternating-impact rhythm in this benchmark.

### pumping

- A hand-designed heuristic that attempts to inject energy based on the sign of the angle and angular velocity, while damping near the middle crossing.
- Evaluated across `z_penalty` and `swing_growth`, with restitution values `1.0`, `0.95`, `0.9`, and `0.8`.
- Result:
  `Alt. = 0` and `Streak = 0` in every tested setting.
- Interpretation:
  A simple energy-pumping heuristic is still insufficient to sustain the desired alternating-impact behavior.

### phase_pumping

- A phase-based heuristic that uses the state-derived oscillation phase together with light pivot feedback.
- Evaluated across `z_penalty` and `swing_growth`, with restitution values `1.0`, `0.95`, `0.9`, and `0.8`.
- Result:
  `Alt. = 0` and `Streak = 0` in every tested setting, with very large `Max |z|` around `7.6`.
- Interpretation:
  A naive phase-based pumping heuristic can inject too much poorly regulated energy and produces a strong blow-up failure mode rather than sustained rhythmic success.

### SAC

- An exploratory SAC sweep was attempted on Thursday, July 16, 2026.
- Status:
  the long run and a reduced-budget exploratory run were both stopped before a complete first benchmark result was produced.
- Interpretation:
  under the current implementation and training budget, SAC appears substantially slower to evaluate in this benchmark than PPO and A2C.

## Failure Taxonomy

The current experiments suggest at least four recurring failure modes.

| Failure mode | Metric signature | Typical examples | Interpretation |
| --- | --- | --- | --- |
| Near-stationary collapse | `Alt. = 0`, `Streak = 0`, low `Max |z|` | `PPO + z_penalty`; `PPO + swing_growth` at `e = 0.9` and `e = 0.8` | The controller remains stable, but it does not build enough oscillatory energy to sustain alternating impacts. |
| Drift-dominated failure | moderate or high `Alt.` possible, large `Max |z|`, often poor or unstable `reward_sum` | several `A2C` runs under `z_penalty` and `swing_growth` | Rhythmic behavior may emerge, but vertical pivot regulation is too weak for the behavior to count as well controlled. |
| Transient rhythmic burst | positive `Alt.`, moderate `Streak`, does not consistently satisfy `Success@10` | `PPO + swing_growth` at high restitution; weaker `A2C` seeds at intermediate restitution | The controller finds the alternating-impact rhythm only temporarily and fails to preserve it for the full rollout. |
| High-energy blow-up | very large `Max |z|`, highly variable `reward_sum`, can coexist with either success or failure on `Alt.` | phase-pumping heuristic; unstable `A2C` seeds with large drift spikes | The controller injects energy too aggressively, producing very large excursions and unstable regulation. |

This should be read as an empirical taxonomy for the current study, not as a proof that every possible failure mode has already been exhausted.

## Failure-Mode Summary by Controller Family

- `PPO`:
  mostly near-stationary collapse, with occasional transient rhythmic bursts under `swing_growth`.
- `A2C`:
  best rhythmic performance overall, but often transitions into drift-dominated or high-energy behavior.
- `Sinusoidal`, `Random`, `Pumping`:
  no meaningful rhythmic success under the current benchmark settings.
