"""
ESPiritAi Self-Upgrading Algorithms

Implements reinforcement learning (RL) and meta-learning components for
continuous self-improvement of the ESPiritAi system.
"""

from __future__ import annotations

import math
import random
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Experience / Replay Buffer
# ---------------------------------------------------------------------------

@dataclass
class Experience:
    """Single transition stored in the replay buffer."""

    state: Any
    action: str
    reward: float
    next_state: Any
    done: bool
    timestamp: float = field(default_factory=time.time)


class ReplayBuffer:
    """Fixed-size experience replay buffer for RL training."""

    def __init__(self, capacity: int = 10_000) -> None:
        self._buffer: deque = deque(maxlen=capacity)

    def push(self, experience: Experience) -> None:
        self._buffer.append(experience)

    def sample(self, batch_size: int) -> List[Experience]:
        n = min(batch_size, len(self._buffer))
        return random.sample(list(self._buffer), n)

    def __len__(self) -> int:
        return len(self._buffer)


# ---------------------------------------------------------------------------
# Reinforcement Learner (tabular Q-learning)
# ---------------------------------------------------------------------------

class ReinforcementLearner:
    """
    Tabular Q-learning agent that learns optimal actions for ESPiritAi
    orchestration tasks.

    States and actions are represented as strings to keep the implementation
    dependency-free while still being fully functional.
    """

    def __init__(
        self,
        actions: List[str],
        learning_rate: float = 0.1,
        discount: float = 0.95,
        epsilon: float = 1.0,
        epsilon_min: float = 0.05,
        epsilon_decay: float = 0.995,
        replay_capacity: int = 10_000,
    ) -> None:
        self.actions = actions
        self.lr = learning_rate
        self.gamma = discount
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self._q: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {a: 0.0 for a in self.actions}
        )
        self.replay = ReplayBuffer(replay_capacity)
        self.episode_rewards: List[float] = []
        self._current_episode_reward: float = 0.0

    # -- Action selection --------------------------------------------------

    def select_action(self, state: str) -> str:
        """Epsilon-greedy action selection."""
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        return max(self._q[state], key=lambda a: self._q[state][a])

    # -- Learning update ---------------------------------------------------

    def update(
        self,
        state: str,
        action: str,
        reward: float,
        next_state: str,
        done: bool,
    ) -> float:
        """Q-learning update; returns TD error."""
        exp = Experience(state, action, reward, next_state, done)
        self.replay.push(exp)
        self._current_episode_reward += reward

        # Q-learning update
        best_next = max(self._q[next_state].values())
        target = reward + (0 if done else self.gamma * best_next)
        td_error = target - self._q[state][action]
        self._q[state][action] += self.lr * td_error

        if done:
            self.episode_rewards.append(self._current_episode_reward)
            self._current_episode_reward = 0.0
            self._decay_epsilon()

        return td_error

    def _decay_epsilon(self) -> None:
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    # -- Batch replay training ---------------------------------------------

    def train_on_batch(self, batch_size: int = 32) -> float:
        """Sample from replay buffer and run batch Q-learning updates."""
        if len(self.replay) < batch_size:
            return 0.0
        batch = self.replay.sample(batch_size)
        total_error = 0.0
        for exp in batch:
            total_error += abs(
                self.update(exp.state, exp.action, exp.reward, exp.next_state, exp.done)
            )
        return total_error / len(batch)

    # -- Metrics -----------------------------------------------------------

    def metrics(self) -> Dict[str, Any]:
        return {
            "epsilon": round(self.epsilon, 4),
            "q_table_states": len(self._q),
            "replay_buffer_size": len(self.replay),
            "episodes_completed": len(self.episode_rewards),
            "avg_reward_last_10": (
                sum(self.episode_rewards[-10:]) / len(self.episode_rewards[-10:])
                if self.episode_rewards
                else 0.0
            ),
        }


# ---------------------------------------------------------------------------
# Meta-Learner (MAML-inspired)
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A meta-learning task consisting of support and query examples."""

    name: str
    support: List[Tuple[Any, float]]  # (input, target_reward)
    query: List[Tuple[Any, float]]


class MetaLearner:
    """
    Model-Agnostic Meta-Learning (MAML)-inspired learner.

    Maintains a set of task-specific adapters on top of a shared parameter
    vector so that ESPiritAi can quickly adapt to new ESP environments or
    operational objectives with only a few examples.
    """

    def __init__(
        self,
        param_dim: int = 64,
        inner_lr: float = 0.01,
        outer_lr: float = 0.001,
        inner_steps: int = 5,
    ) -> None:
        # Shared meta-parameters (simple vector as stand-in for model weights)
        self.meta_params: List[float] = [random.gauss(0, 0.1) for _ in range(param_dim)]
        self.inner_lr = inner_lr
        self.outer_lr = outer_lr
        self.inner_steps = inner_steps
        self.adaptation_history: List[Dict[str, Any]] = []

    def _predict(self, params: List[float], x: Any) -> float:
        """Simple dot-product predictor (placeholder for a real model)."""
        if isinstance(x, (list, tuple)):
            features = [float(v) for v in x]
        else:
            # Hash the input to a stable feature vector
            seed = hash(str(x)) % (2 ** 32)
            rng = random.Random(seed)
            features = [rng.gauss(0, 1) for _ in range(len(params))]
        dot = sum(p * f for p, f in zip(params, features))
        return math.tanh(dot)  # squash to (-1, 1)

    def _loss(
        self, params: List[float], examples: List[Tuple[Any, float]]
    ) -> float:
        """MSE loss over examples."""
        if not examples:
            return 0.0
        return sum((self._predict(params, x) - y) ** 2 for x, y in examples) / len(
            examples
        )

    def _grad(
        self, params: List[float], examples: List[Tuple[Any, float]], eps: float = 1e-4
    ) -> List[float]:
        """Numerical gradient via finite differences."""
        base_loss = self._loss(params, examples)
        grads = []
        for i in range(len(params)):
            params[i] += eps
            perturbed = self._loss(params, examples)
            params[i] -= eps
            grads.append((perturbed - base_loss) / eps)
        return grads

    def adapt(self, task: Task) -> List[float]:
        """Inner-loop adaptation: fine-tune meta_params on task support set."""
        adapted = list(self.meta_params)
        for _ in range(self.inner_steps):
            grads = self._grad(adapted, task.support)
            adapted = [p - self.inner_lr * g for p, g in zip(adapted, grads)]
        return adapted

    def meta_update(self, tasks: List[Task]) -> float:
        """
        Outer-loop update: average query-set gradients across tasks and
        update meta_params.
        """
        if not tasks:
            return 0.0
        meta_grads = [0.0] * len(self.meta_params)
        total_loss = 0.0
        for task in tasks:
            adapted = self.adapt(task)
            query_grads = self._grad(adapted, task.query)
            total_loss += self._loss(adapted, task.query)
            for i, g in enumerate(query_grads):
                meta_grads[i] += g
        n = len(tasks)
        self.meta_params = [
            p - self.outer_lr * (g / n)
            for p, g in zip(self.meta_params, meta_grads)
        ]
        avg_loss = total_loss / n
        self.adaptation_history.append(
            {"tasks": n, "avg_query_loss": round(avg_loss, 6)}
        )
        return avg_loss

    def metrics(self) -> Dict[str, Any]:
        return {
            "param_dim": len(self.meta_params),
            "meta_updates": len(self.adaptation_history),
            "last_avg_query_loss": (
                self.adaptation_history[-1]["avg_query_loss"]
                if self.adaptation_history
                else None
            ),
        }


# ---------------------------------------------------------------------------
# Self-Upgrader
# ---------------------------------------------------------------------------

class SelfUpgrader:
    """
    Orchestrates continuous self-improvement of ESPiritAi by running RL
    and meta-learning cycles, tracking performance, and applying upgrades
    when a performance threshold is reached.
    """

    UPGRADE_THRESHOLD = 0.8  # avg reward fraction that triggers an upgrade

    def __init__(
        self,
        rl_actions: Optional[List[str]] = None,
        meta_param_dim: int = 64,
    ) -> None:
        default_actions = [
            "optimize_scan",
            "switch_engine_speed",
            "redistribute_tasks",
            "update_knowledge",
            "retrain_council",
            "adjust_simulation_params",
        ]
        self.rl = ReinforcementLearner(rl_actions or default_actions)
        self.meta = MetaLearner(param_dim=meta_param_dim)
        self.upgrade_log: List[Dict[str, Any]] = []
        self._cycle_count: int = 0

    def run_cycle(
        self,
        state: str,
        reward_fn: Callable[[str, str], float],
        meta_tasks: Optional[List[Task]] = None,
    ) -> Dict[str, Any]:
        """
        Run one self-upgrade cycle:
          1. RL agent selects and evaluates an action.
          2. Meta-learner updates on provided tasks (if any).
          3. Check upgrade threshold and log.
        """
        self._cycle_count += 1
        action = self.rl.select_action(state)
        reward = reward_fn(state, action)
        next_state = f"{state}_{action}"
        done = self._cycle_count % 10 == 0  # end episode every 10 cycles
        td_error = self.rl.update(state, action, reward, next_state, done)

        meta_loss = None
        if meta_tasks:
            meta_loss = self.meta.meta_update(meta_tasks)

        # Check for upgrade
        rl_metrics = self.rl.metrics()
        avg_reward = rl_metrics.get("avg_reward_last_10", 0.0)
        if avg_reward >= self.UPGRADE_THRESHOLD:
            self._apply_upgrade(avg_reward)

        return {
            "cycle": self._cycle_count,
            "action": action,
            "reward": reward,
            "td_error": round(td_error, 6),
            "meta_loss": meta_loss,
            "rl_metrics": rl_metrics,
        }

    def _apply_upgrade(self, trigger_reward: float) -> None:
        """Record an upgrade event (hook for future model-swap logic)."""
        entry = {
            "cycle": self._cycle_count,
            "trigger_reward": trigger_reward,
            "timestamp": time.time(),
        }
        self.upgrade_log.append(entry)

    def metrics(self) -> Dict[str, Any]:
        return {
            "cycles": self._cycle_count,
            "upgrades_applied": len(self.upgrade_log),
            "rl": self.rl.metrics(),
            "meta": self.meta.metrics(),
        }
