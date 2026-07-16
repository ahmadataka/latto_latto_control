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
