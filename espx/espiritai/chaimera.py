"""
CHAIMERA - Custom Hybrid AI Framework

Blends multiple AI paradigms (symbolic reasoning, fuzzy logic,
neural/statistical models, and evolutionary algorithms) into a single
unified inference engine for ESPiritAi.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Paradigm identifiers
# ---------------------------------------------------------------------------

class Paradigm(str, Enum):
    SYMBOLIC = "symbolic"          # rule-based / expert-system
    FUZZY = "fuzzy"                # fuzzy logic
    STATISTICAL = "statistical"    # Bayesian / probabilistic
    EVOLUTIONARY = "evolutionary"  # genetic / evolutionary algorithms
    NEURAL = "neural"              # lightweight neural / perceptron


# ---------------------------------------------------------------------------
# Symbolic reasoning (rule engine)
# ---------------------------------------------------------------------------

@dataclass
class Rule:
    """A symbolic IF-THEN rule."""

    name: str
    condition: Callable[[Dict[str, Any]], bool]
    action: str
    confidence: float = 1.0
    priority: int = 0  # higher = more important


class SymbolicReasoner:
    """Simple forward-chaining rule engine."""

    def __init__(self) -> None:
        self.rules: List[Rule] = []

    def add_rule(self, rule: Rule) -> None:
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def infer(self, facts: Dict[str, Any]) -> Optional[Tuple[str, float]]:
        """Return the first matching (action, confidence) or None."""
        for rule in self.rules:
            try:
                if rule.condition(facts):
                    return rule.action, rule.confidence
            except Exception:  # pylint: disable=broad-except
                continue
        return None


# ---------------------------------------------------------------------------
# Fuzzy logic
# ---------------------------------------------------------------------------

class FuzzyVariable:
    """Triangular membership function fuzzy variable."""

    def __init__(self, name: str, low: float, mid: float, high: float) -> None:
        self.name = name
        self.low = low
        self.mid = mid
        self.high = high

    def membership(self, value: float) -> float:
        """Return degree of membership ∈ [0, 1]."""
        if value <= self.low or value >= self.high:
            return 0.0
        if value <= self.mid:
            return (value - self.low) / (self.mid - self.low)
        return (self.high - value) / (self.high - self.mid)


class FuzzyInference:
    """Minimal Mamdani fuzzy inference system."""

    def __init__(self) -> None:
        self.variables: Dict[str, FuzzyVariable] = {}
        self._rules: List[Tuple[str, str, str]] = []  # (input_var, output_action)

    def add_variable(self, var: FuzzyVariable) -> None:
        self.variables[var.name] = var

    def add_rule(self, input_var: str, output_action: str) -> None:
        self._rules.append((input_var, output_action))

    def infer(self, inputs: Dict[str, float]) -> Optional[Tuple[str, float]]:
        """Return (action, degree) for the rule with the highest activation."""
        best_action: Optional[str] = None
        best_degree: float = 0.0
        for var_name, action in self._rules:
            var = self.variables.get(var_name)
            value = inputs.get(var_name, 0.0)
            degree = var.membership(value) if var else 0.0
            if degree > best_degree:
                best_degree = degree
                best_action = action
        if best_action is None:
            return None
        return best_action, best_degree


# ---------------------------------------------------------------------------
# Statistical / Bayesian component
# ---------------------------------------------------------------------------

class BayesianClassifier:
    """
    Naïve Bayes classifier for discrete action selection based on
    observed feature distributions.
    """

    def __init__(self, actions: List[str]) -> None:
        self.actions = actions
        # Prior counts for each action
        self._counts: Dict[str, int] = {a: 1 for a in actions}  # Laplace smoothing
        self._feature_counts: Dict[str, Dict[str, Dict[Any, int]]] = {
            a: {} for a in actions
        }

    def train(self, features: Dict[str, Any], action: str) -> None:
        if action not in self._counts:
            return
        self._counts[action] += 1
        for feat, val in features.items():
            if feat not in self._feature_counts[action]:
                self._feature_counts[action][feat] = {}
            v = str(val)
            self._feature_counts[action][feat][v] = (
                self._feature_counts[action][feat].get(v, 0) + 1
            )

    def predict(self, features: Dict[str, Any]) -> Tuple[str, float]:
        total = sum(self._counts.values())
        scores: Dict[str, float] = {}
        for action in self.actions:
            log_prob = math.log(self._counts[action] / total)
            for feat, val in features.items():
                feat_dist = self._feature_counts[action].get(feat, {})
                feat_total = sum(feat_dist.values()) + len(feat_dist) + 1
                feat_count = feat_dist.get(str(val), 0) + 1
                log_prob += math.log(feat_count / feat_total)
            scores[action] = log_prob
        best = max(scores, key=lambda a: scores[a])
        # Softmax-style probability
        exp_scores = {a: math.exp(s - scores[best]) for a, s in scores.items()}
        total_exp = sum(exp_scores.values())
        confidence = exp_scores[best] / total_exp
        return best, round(confidence, 4)


# ---------------------------------------------------------------------------
# Evolutionary / genetic algorithm component
# ---------------------------------------------------------------------------

@dataclass
class Individual:
    """A candidate solution in the evolutionary algorithm."""

    genes: List[float]
    fitness: float = 0.0


class EvolutionaryOptimiser:
    """
    Simple genetic algorithm for optimising continuous parameters
    (e.g., engine speed settings, council weights).
    """

    def __init__(
        self,
        param_dim: int,
        pop_size: int = 20,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.7,
    ) -> None:
        self.param_dim = param_dim
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.population: List[Individual] = [
            Individual(genes=[random.gauss(0, 1) for _ in range(param_dim)])
            for _ in range(pop_size)
        ]
        self.generation: int = 0
        self.best: Optional[Individual] = None

    def evolve(self, fitness_fn: Callable[[List[float]], float]) -> Individual:
        """Run one generation; return best individual."""
        # Evaluate
        for ind in self.population:
            ind.fitness = fitness_fn(ind.genes)

        # Track best
        current_best = max(self.population, key=lambda i: i.fitness)
        if self.best is None or current_best.fitness > self.best.fitness:
            self.best = Individual(
                genes=list(current_best.genes), fitness=current_best.fitness
            )

        # Selection (tournament)
        new_pop: List[Individual] = []
        while len(new_pop) < self.pop_size:
            a, b = random.sample(self.population, 2)
            parent = a if a.fitness >= b.fitness else b
            new_pop.append(Individual(genes=list(parent.genes)))

        # Crossover + mutation
        for i in range(0, len(new_pop) - 1, 2):
            if random.random() < self.crossover_rate:
                pt = random.randint(1, self.param_dim - 1)
                new_pop[i].genes[pt:], new_pop[i + 1].genes[pt:] = (
                    new_pop[i + 1].genes[pt:],
                    new_pop[i].genes[pt:],
                )
            for ind in (new_pop[i], new_pop[i + 1]):
                for j in range(self.param_dim):
                    if random.random() < self.mutation_rate:
                        ind.genes[j] += random.gauss(0, 0.3)

        self.population = new_pop
        self.generation += 1
        return self.best  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Neural component (single-layer perceptron)
# ---------------------------------------------------------------------------

class Perceptron:
    """Single-layer perceptron for binary / softmax classification."""

    def __init__(self, input_dim: int, output_dim: int, lr: float = 0.01) -> None:
        self.weights: List[List[float]] = [
            [random.gauss(0, 0.1) for _ in range(input_dim)]
            for _ in range(output_dim)
        ]
        self.biases: List[float] = [0.0] * output_dim
        self.lr = lr

    def _softmax(self, logits: List[float]) -> List[float]:
        max_l = max(logits)
        exps = [math.exp(l - max_l) for l in logits]
        total = sum(exps)
        return [e / total for e in exps]

    def forward(self, x: List[float]) -> List[float]:
        logits = [
            sum(w * xi for w, xi in zip(row, x)) + b
            for row, b in zip(self.weights, self.biases)
        ]
        return self._softmax(logits)

    def train_step(self, x: List[float], target_idx: int) -> float:
        probs = self.forward(x)
        # Cross-entropy gradient
        loss = -math.log(max(probs[target_idx], 1e-9))
        for i, (row, b) in enumerate(zip(self.weights, self.biases)):
            grad = probs[i] - (1.0 if i == target_idx else 0.0)
            for j in range(len(row)):
                self.weights[i][j] -= self.lr * grad * x[j]
            self.biases[i] -= self.lr * grad
        return loss


# ---------------------------------------------------------------------------
# CHAIMERA – blended inference
# ---------------------------------------------------------------------------

@dataclass
class ChaimeraResult:
    """Aggregated inference result from CHAIMERA."""

    final_action: str
    confidence: float
    paradigm_votes: Dict[str, Optional[Tuple[str, float]]]
    blend_weights: Dict[str, float]


class CHAIMERA:
    """
    Custom Hybrid AI fRAMEwoRk – blends symbolic, fuzzy, statistical,
    evolutionary, and neural paradigms into a single inference engine.
    """

    DEFAULT_WEIGHTS: Dict[str, float] = {
        Paradigm.SYMBOLIC: 0.30,
        Paradigm.FUZZY: 0.15,
        Paradigm.STATISTICAL: 0.25,
        Paradigm.EVOLUTIONARY: 0.10,
        Paradigm.NEURAL: 0.20,
    }

    def __init__(
        self,
        actions: List[str],
        blend_weights: Optional[Dict[str, float]] = None,
        evolve_generations: int = 5,
    ) -> None:
        self.actions = actions
        self.blend_weights: Dict[str, float] = blend_weights or dict(
            self.DEFAULT_WEIGHTS
        )
        self._evolve_generations = evolve_generations

        # Initialise each paradigm component
        self.symbolic = SymbolicReasoner()
        self.fuzzy = FuzzyInference()
        self.statistical = BayesianClassifier(actions)
        self.evolutionary = EvolutionaryOptimiser(param_dim=len(actions))
        self.neural = Perceptron(input_dim=8, output_dim=len(actions))

        self._setup_default_rules()

    def _setup_default_rules(self) -> None:
        """Register sensible default symbolic and fuzzy rules."""
        # Symbolic rules
        self.symbolic.add_rule(Rule(
            name="high_risk_abort",
            condition=lambda f: f.get("risk_score", 0.0) > 0.75,
            action="abort",
            confidence=0.95,
            priority=10,
        ))
        self.symbolic.add_rule(Rule(
            name="low_heap_reduce",
            condition=lambda f: f.get("heap_free_b", 200_000) < 20_000,
            action="reduce_load",
            confidence=0.90,
            priority=9,
        ))

        # Fuzzy variables
        self.fuzzy.add_variable(FuzzyVariable("cpu_usage_pct", 60, 80, 100))
        self.fuzzy.add_variable(FuzzyVariable("risk_score", 0.4, 0.6, 0.8))
        self.fuzzy.add_rule("cpu_usage_pct", "reduce_load")
        self.fuzzy.add_rule("risk_score", "abort")

    def infer(self, context: Dict[str, Any]) -> ChaimeraResult:
        """
        Run all paradigms and blend their outputs via weighted voting.
        """
        votes: Dict[str, float] = {a: 0.0 for a in self.actions}
        paradigm_votes: Dict[str, Optional[Tuple[str, float]]] = {}

        # 1. Symbolic
        sym_result = self.symbolic.infer(context)
        paradigm_votes[Paradigm.SYMBOLIC] = sym_result
        if sym_result and sym_result[0] in votes:
            votes[sym_result[0]] += self.blend_weights[Paradigm.SYMBOLIC] * sym_result[1]

        # 2. Fuzzy
        fuz_result = self.fuzzy.infer(
            {k: float(v) for k, v in context.items() if isinstance(v, (int, float))}
        )
        paradigm_votes[Paradigm.FUZZY] = fuz_result
        if fuz_result and fuz_result[0] in votes:
            votes[fuz_result[0]] += self.blend_weights[Paradigm.FUZZY] * fuz_result[1]

        # 3. Statistical
        features = {k: v for k, v in context.items() if isinstance(v, (int, float, bool, str))}
        stat_action, stat_conf = self.statistical.predict(features)
        paradigm_votes[Paradigm.STATISTICAL] = (stat_action, stat_conf)
        if stat_action in votes:
            votes[stat_action] += self.blend_weights[Paradigm.STATISTICAL] * stat_conf

        # 4. Evolutionary (use best individual's gene index as action vote)
        def fitness_fn(genes: List[float]) -> float:
            idx = genes.index(max(genes)) if genes else 0
            return context.get("reward", 0.5) * abs(sum(genes))

        for _ in range(self._evolve_generations):
            best = self.evolutionary.evolve(fitness_fn)
        if best and best.genes:
            evo_idx = best.genes.index(max(best.genes)) % len(self.actions)
            evo_action = self.actions[evo_idx]
            paradigm_votes[Paradigm.EVOLUTIONARY] = (evo_action, best.fitness)
            if evo_action in votes:
                votes[evo_action] += self.blend_weights[Paradigm.EVOLUTIONARY] * min(
                    1.0, best.fitness
                )

        # 5. Neural
        x = [
            context.get("risk_score", 0.0),
            context.get("cpu_usage_pct", 0.0) / 100.0,
            context.get("heap_free_b", 200_000) / 200_000.0,
            float(context.get("wifi_connected", False)),
            context.get("reward", 0.5),
            0.0, 0.0, 0.0,  # reserved features
        ]
        neural_probs = self.neural.forward(x)
        best_neural_idx = neural_probs.index(max(neural_probs))
        neural_action = self.actions[best_neural_idx]
        paradigm_votes[Paradigm.NEURAL] = (neural_action, neural_probs[best_neural_idx])
        votes[neural_action] += (
            self.blend_weights[Paradigm.NEURAL] * neural_probs[best_neural_idx]
        )

        # Final decision
        total = sum(votes.values()) or 1.0
        final_action = max(votes, key=lambda a: votes[a])
        confidence = round(votes[final_action] / total, 4)

        return ChaimeraResult(
            final_action=final_action,
            confidence=confidence,
            paradigm_votes=paradigm_votes,
            blend_weights=dict(self.blend_weights),
        )

    def feedback(self, context: Dict[str, Any], chosen_action: str, reward: float) -> None:
        """Update statistical and neural components from feedback."""
        features = {
            k: v for k, v in context.items()
            if isinstance(v, (int, float, bool, str))
        }
        if chosen_action in self.statistical.actions:
            self.statistical.train(features, chosen_action)
        # Neural update
        action_idx = (
            self.actions.index(chosen_action)
            if chosen_action in self.actions
            else 0
        )
        x = [
            context.get("risk_score", 0.0),
            context.get("cpu_usage_pct", 0.0) / 100.0,
            context.get("heap_free_b", 200_000) / 200_000.0,
            float(context.get("wifi_connected", False)),
            reward,
            0.0, 0.0, 0.0,
        ]
        if reward > 0:
            self.neural.train_step(x, action_idx)

    def metrics(self) -> Dict[str, Any]:
        return {
            "actions": self.actions,
            "blend_weights": self.blend_weights,
            "evolutionary_generation": self.evolutionary.generation,
            "symbolic_rules": len(self.symbolic.rules),
            "bayesian_trained_samples": sum(
                self.statistical._counts.values()
            ),
        }
