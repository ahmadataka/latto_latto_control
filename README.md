# Latto-Latto Control Research Repo

This repository studies control of a simplified Latto-latto system with a vertically actuated pivot, hybrid collision dynamics, and PPO-based reinforcement learning experiments.

The current research status is:
- the repository now has a cleaner experiment structure
- multiple reward and collision-model sweeps have been run
- the rhythmic alternating-collision behavior is still not solved
- further reward-design work is still needed

## Project Structure

```text
latto_latto_control/
├── src/
│   └── latto_latto_model.py
├── scripts/
│   ├── training_latto_ppo.py
│   ├── testing_latto.py
│   ├── alpha_sweep_experiment.py
│   ├── ztol_sweep_experiment.py
│   └── collision_reward_sweep_experiment.py
├── models/
│   ├── baselines/
│   ├── alpha_sweep/
│   ├── alpha_sweep_inelastic/
│   ├── ztol_sweep_inelastic/
│   └── collision_reward_sweep_inelastic/
├── results/
│   ├── testing/
│   ├── alpha_sweep/
│   ├── alpha_sweep_inelastic/
│   ├── ztol_sweep_inelastic/
│   └── collision_reward_sweep_inelastic/
├── docs/
│   ├── RESEARCH_CHANGELOG.md
│   ├── RESEARCH_CHANGELOG.tex
│   └── RESEARCH_CHANGELOG.pdf
├── references/
│   └── 3007.full.pdf
└── .gitignore
```

## Main Files

- [src/latto_latto_model.py](/Users/ahmadataka/Documents/Bitbucket%20-%20Ataka/latto_latto_control/src/latto_latto_model.py:1): Gym environment, reward logic, and collision model.
- [src/benchmark_utils.py](/Users/ahmadataka/Documents/Bitbucket%20-%20Ataka/latto_latto_control/src/benchmark_utils.py:1): shared training/evaluation helpers and benchmark metrics.
- [scripts/training_latto_ppo.py](/Users/ahmadataka/Documents/Bitbucket%20-%20Ataka/latto_latto_control/scripts/training_latto_ppo.py:1): baseline PPO training entrypoint.
- [scripts/testing_latto.py](/Users/ahmadataka/Documents/Bitbucket%20-%20Ataka/latto_latto_control/scripts/testing_latto.py:1): rollout animation and testing plots.
- [scripts/run_benchmark_experiment.py](/Users/ahmadataka/Documents/Bitbucket%20-%20Ataka/latto_latto_control/scripts/run_benchmark_experiment.py:1): seed-aware benchmark runner with standardized JSON outputs.
- [docs/RESEARCH_CHANGELOG.pdf](/Users/ahmadataka/Documents/Bitbucket%20-%20Ataka/latto_latto_control/docs/RESEARCH_CHANGELOG.pdf): rendered research log with equations.

## Setup

- Python 3
- `numpy`
- `matplotlib`
- `gym`
- `stable-baselines3`

The repo already uses a local `.venv`, so the standard way to run scripts is with:

```bash
cd "/Users/ahmadataka/Documents/Bitbucket - Ataka/latto_latto_control"
.venv/bin/python scripts/<script_name>.py
```

## How To Run

### Train the current baseline PPO

```bash
cd "/Users/ahmadataka/Documents/Bitbucket - Ataka/latto_latto_control"
MPLCONFIGDIR=/private/tmp .venv/bin/python scripts/training_latto_ppo.py
```

This saves the baseline checkpoint to:
- `models/baselines/ppo_latto_z_penalty.zip`

### Visualize a trained model

Default baseline model:

```bash
cd "/Users/ahmadataka/Documents/Bitbucket - Ataka/latto_latto_control"
.venv/bin/python scripts/testing_latto.py
```

Specific model:

```bash
cd "/Users/ahmadataka/Documents/Bitbucket - Ataka/latto_latto_control"
.venv/bin/python scripts/testing_latto.py models/ztol_sweep_inelastic/ppo_latto_inelastic_ztol_0p080
```

This generates:
- `results/testing/testing_action_trace.png`
- `results/testing/testing_pose_trace.png`
- `results/testing/testing_metrics.json`

### Run the benchmark runner

This is the main paper-oriented experiment entrypoint. It trains one algorithm across one or more seeds and saves per-seed metrics plus a summary JSON.

```bash
cd "/Users/ahmadataka/Documents/Bitbucket - Ataka/latto_latto_control"
MPLCONFIGDIR=/private/tmp .venv/bin/python scripts/run_benchmark_experiment.py \
  --algorithm ppo \
  --reward-variant z_penalty \
  --seeds 0 1 2 \
  --collision-restitution 0.9
```

### Aggregate benchmark results

```bash
cd "/Users/ahmadataka/Documents/Bitbucket - Ataka/latto_latto_control"
.venv/bin/python scripts/aggregate_benchmark_results.py
```

### Run experiment sweeps

Alpha sweep on the inelastic model:

```bash
MPLBACKEND=Agg MPLCONFIGDIR=/private/tmp .venv/bin/python scripts/alpha_sweep_experiment.py
```

`z_tol` dead-zone sweep:

```bash
MPLBACKEND=Agg MPLCONFIGDIR=/private/tmp .venv/bin/python scripts/ztol_sweep_experiment.py
```

Collision reward weight sweep:

```bash
MPLBACKEND=Agg MPLCONFIGDIR=/private/tmp .venv/bin/python scripts/collision_reward_sweep_experiment.py
```

## Experiment Artifacts

This section intentionally uses explicit filenames to avoid confusion.

### Benchmark metrics now tracked

- `alternating_collisions`
- `longest_alternating_streak`
- `total_collisions`
- `time_to_first_alternating_collision`
- `reward_sum`
- `mean_abs_z`
- `max_abs_z`
- `mean_collision_energy_loss`

### Baseline testing outputs

- Generated action trace: `results/testing/testing_action_trace.png`
- Generated pose trace: `results/testing/testing_pose_trace.png`

### Reward-weight comparison files

- Generated ideal/inelastic alpha sweep comparison plot:
  `results/alpha_sweep_inelastic/alpha_pose_inelastic_comparison.png`
- Ideal/inelastic alpha sweep summary:
  `results/alpha_sweep_inelastic/alpha_sweep_inelastic_results.json`

### Dead-zone tolerance comparison files

- Generated `z_tol` sweep comparison plot:
  `results/ztol_sweep_inelastic/ztol_pose_inelastic_comparison.png`
- `z_tol` sweep summary:
  `results/ztol_sweep_inelastic/ztol_sweep_inelastic_results.json`

### Collision reward weight comparison files

- Generated collision reward sweep comparison plot:
  `results/collision_reward_sweep_inelastic/collision_reward_pose_inelastic_comparison.png`
- Collision reward sweep summary:
  `results/collision_reward_sweep_inelastic/collision_reward_sweep_inelastic_results.json`

Note:
- PNG plots are generated artifacts and are intentionally not kept in Git.
- JSON summaries and trained checkpoints remain in the repository for experiment traceability.

## Trained Model Locations

### Baselines

- `models/baselines/ppo_latto.zip`
- `models/baselines/ppo_latto_z_penalty.zip`

### Alpha sweep on earlier reward design

- `models/alpha_sweep/ppo_latto_alpha_0p010.zip`
- `models/alpha_sweep/ppo_latto_alpha_0p020.zip`
- `models/alpha_sweep/ppo_latto_alpha_0p050.zip`

### Alpha sweep on inelastic collision model

- `models/alpha_sweep_inelastic/ppo_latto_inelastic_alpha_0p010.zip`
- `models/alpha_sweep_inelastic/ppo_latto_inelastic_alpha_0p020.zip`
- `models/alpha_sweep_inelastic/ppo_latto_inelastic_alpha_0p050.zip`

### Dead-zone `z_tol` sweep

- `models/ztol_sweep_inelastic/ppo_latto_inelastic_ztol_0p030.zip`
- `models/ztol_sweep_inelastic/ppo_latto_inelastic_ztol_0p050.zip`
- `models/ztol_sweep_inelastic/ppo_latto_inelastic_ztol_0p080.zip`

### Collision reward weight sweep

- `models/collision_reward_sweep_inelastic/ppo_latto_inelastic_wc_1p0.zip`
- `models/collision_reward_sweep_inelastic/ppo_latto_inelastic_wc_2p0.zip`
- `models/collision_reward_sweep_inelastic/ppo_latto_inelastic_wc_5p0.zip`

## Documentation

- Working changelog notes:
  [docs/RESEARCH_CHANGELOG.md](/Users/ahmadataka/Documents/Bitbucket%20-%20Ataka/latto_latto_control/docs/RESEARCH_CHANGELOG.md:1)
- LaTeX source:
  [docs/RESEARCH_CHANGELOG.tex](/Users/ahmadataka/Documents/Bitbucket%20-%20Ataka/latto_latto_control/docs/RESEARCH_CHANGELOG.tex:1)
- Rendered PDF:
  [docs/RESEARCH_CHANGELOG.pdf](/Users/ahmadataka/Documents/Bitbucket%20-%20Ataka/latto_latto_control/docs/RESEARCH_CHANGELOG.pdf)

## Current Research Note

The repository now has clearer structure, but the control problem is still unresolved. The recent sweeps suggest that changing penalty weight, dead-zone width, and collision reward weight alone is not enough. The next likely direction is a reward term that encourages swing growth before alternating collisions appear.

## Reward Variants

The environment now supports explicit reward families through `reward_variant`:

- `sparse_only`: reward only for alternating collisions.
- `z_penalty`: alternating-collision reward minus pivot drift penalty.
- `deadzone`: same penalty form, intended for use with nonzero `z_position_tolerance`.
- `swing_growth`: `z_penalty` reward plus a positive bonus when swing amplitude grows toward the impact regime.
