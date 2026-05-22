# Research Changelog

This document records major changes to the Latto-latto model, reward design, and training setup.

Rule for future updates:
- Any major change to the model, reward, controller, training setup, or evaluation protocol should be added to this file.

## 2026-05-22

### Change 1: Reward updated to penalize vertical drift

Motivation:
- The original sparse reward was able to produce bouncing behavior, but the pivot vertical position `z` could drift over time.
- This made the learned behavior less physically meaningful and less suitable for fair controller comparison.

Previous reward:

\[
r_t =
\begin{cases}
1, & \text{if a collision occurs and the collision side alternates} \\
0, & \text{otherwise}
\end{cases}
\]

Updated reward:

\[
r_t = r_t^{\mathrm{collision}} - \alpha z_t^2
\]

with

\[
r_t^{\mathrm{collision}} =
\begin{cases}
1, & \text{if a collision occurs and the collision side alternates} \\
0, & \text{otherwise}
\end{cases}
\]

where:
- `z_t` is the vertical position of the pivot
- `\alpha` is the vertical position penalty weight

Current setting in code:

\[
\alpha = 0.1
\]

Implementation notes:
- The reward is implemented in `latto_latto_model.py`.
- The environment now exposes reward components through the `info` dictionary:
  - `sparse_reward`
  - `z_position_penalty`

Observed outcome:
- PPO training completed successfully with the modified reward.
- The learned policy strongly reduced vertical drift.
- In quick evaluation, the policy also collapsed to a near-stationary solution with zero alternating collisions.

Interpretation:
- The drift penalty successfully regularized the base motion.
- The penalty weight `\alpha = 0.1` appears too strong relative to the sparse collision reward.
- A smaller penalty weight, such as `0.01` or `0.02`, should be tested next.

### Change 2: Separate PPO checkpoint for reward-penalty experiment

Motivation:
- Preserve the original PPO checkpoint while training a new policy with the modified reward.

Change:
- Training output path changed from `ppo_latto` to `ppo_latto_z_penalty`.

Result:
- The reward-penalty experiment can now be evaluated independently from the original sparse-reward PPO model.

### Change 3: Testing script updated to load the new checkpoint

Motivation:
- Keep the default evaluation script aligned with the most recent model variant.

Change:
- `testing_latto.py` now loads `ppo_latto_z_penalty`.

Note:
- If multiple controller/reward variants are added later, this script should eventually accept a model path as an argument instead of hardcoding one checkpoint.

### Change 4: Visualization workflow improved

Motivation:
- The rendering logic was previously tied to repeated global `matplotlib` calls, which was less stable for repeated runs.

Change:
- Rendering now uses persistent `matplotlib` figure and axes handles.
- The environment now includes a `close()` method to release plotting resources cleanly.
- `testing_latto.py` now handles interactive and non-interactive backends more safely.

Research relevance:
- This is not a dynamics change, but it improves repeatability of visual inspection during controller evaluation.

### Change 5: Testing script now plots pose trajectories

Motivation:
- The previous testing workflow only saved the control input history.
- For controller comparison, it is also important to inspect how the pivot position and pendulum angle evolve over time.

Change:
- `testing_latto.py` now records and plots:
  - pivot vertical position `z(t)`
  - pendulum angle `\theta(t)`
- The script now saves an additional figure, `pose.png`.

Research relevance:
- This improves the evaluation workflow by making drift, oscillation amplitude, and near-stationary collapse easier to detect visually.
