# LATTO-LATTO CONTROL BASED ON DEEP REINFORCEMENT LEARNING #

### What is this repository for? ###

This is a repository on controlling a double-pendulum system with vertically-moving base points, a toy popularly known as Latto-latto in Indonesia. The control algorithm is based on deep reinforcement learning algorithm, namely the Proximal Policy Optimization (PPO).

This is the first version, developed by Ahmad Ataka (Twitter: @ahmadataka, Website: ahmadataka.bitbucket.io), a lecturer at Department of Electrical and Information Engineering, Universitas Gadjah Mada, Indonesia.

### How do I get set up? ###

* Python3, including basic libraries such as Numpy, Matplotlib.
* Gym by OpenAI (https://github.com/openai/gym) to setup the model of Latto-latto
* Stable Baselines3 (https://github.com/DLR-RM/stable-baselines3) to implement Deep Reinforcement Learning, especially PPO.

### What's inside the repo? ###

* latto_latto_model.py: a code consisting of Latto-latto's model in Gym environment.
* training_latto_ppo.py: a code to train PPO in Latto-latto environment.
* testing_latto.py: a code for testing the performance of the algorithm.
* alpha_sweep_experiment.py: a script to train and compare multiple PPO models across different vertical drift penalty weights.
* ppo_latto.zip: a PPO model produced by training_latto_ppo.py to generate action for Latto-latto.
* ppo_latto_z_penalty.zip: a PPO model trained with sparse reward plus vertical position penalty.
* 3007.full.pdf: some reference.
* RESEARCH_CHANGELOG.tex: LaTeX source for the research changelog.
* RESEARCH_CHANGELOG.pdf: compiled PDF version of the research changelog with readable equations.
* RESEARCH_CHANGELOG.md: working markdown notes for the changelog content.
