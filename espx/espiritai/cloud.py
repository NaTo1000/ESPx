"""
ESPiritAi Cloud Compute & Hugging Face Integration

Provides cloud compute access for distributed processing and integration
with Hugging Face models for AI enhancements.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


# ---------------------------------------------------------------------------
# Cloud Job
# ---------------------------------------------------------------------------

@dataclass
class CloudJob:
    """A unit of work submitted to the cloud compute layer."""

    job_id: str
    task: str
    payload: Dict[str, Any]
    status: str = "submitted"  # submitted | running | completed | failed
    result: Optional[Dict[str, Any]] = None
    submitted_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None


# ---------------------------------------------------------------------------
# Cloud Compute Client
# ---------------------------------------------------------------------------

class CloudComputeClient:
    """
    Abstraction over a distributed cloud compute backend.

    In production this would integrate with AWS Lambda, GCP Cloud Run,
    Azure Functions, or a custom Kubernetes cluster.  The current
    implementation is a local simulation that supports custom handlers
    registered per task type.
    """

    def __init__(self, endpoint: str = "local://espiritai-cloud") -> None:
        self.endpoint = endpoint
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}
        self._jobs: Dict[str, CloudJob] = {}
        self._job_counter: int = 0
        self.connected: bool = True  # simulated connection state

    # -- Registration ------------------------------------------------------

    def register_task_handler(
        self, task: str, handler: Callable[[Dict[str, Any]], Dict[str, Any]]
    ) -> None:
        """Register a compute handler for a named task type."""
        self._handlers[task] = handler

    # -- Submission --------------------------------------------------------

    def submit(self, task: str, payload: Optional[Dict[str, Any]] = None) -> CloudJob:
        """Submit a job to the cloud compute layer."""
        self._job_counter += 1
        job_id = f"cloud_{self._job_counter:06d}"
        job = CloudJob(job_id=job_id, task=task, payload=payload or {})
        self._jobs[job_id] = job

        if not self.connected:
            job.status = "failed"
            job.result = {"error": "Cloud compute not connected"}
            return job

        # Execute immediately (simulated synchronous dispatch)
        job.status = "running"
        handler = self._handlers.get(task, self._default_handler)
        try:
            job.result = handler(job.payload)
            job.status = "completed"
        except Exception as exc:  # pylint: disable=broad-except
            job.result = {"error": str(exc)}
            job.status = "failed"
        job.completed_at = time.time()
        return job

    def _default_handler(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Default no-op handler that echoes the payload."""
        return {
            "status": "ok",
            "echo": payload,
            "compute_node": self.endpoint,
        }

    # -- Retrieval ---------------------------------------------------------

    def get_job(self, job_id: str) -> Optional[CloudJob]:
        return self._jobs.get(job_id)

    def list_jobs(
        self, status: Optional[str] = None
    ) -> List[CloudJob]:
        jobs = list(self._jobs.values())
        if status:
            jobs = [j for j in jobs if j.status == status]
        return jobs

    # -- Metrics -----------------------------------------------------------

    def metrics(self) -> Dict[str, Any]:
        jobs = list(self._jobs.values())
        return {
            "endpoint": self.endpoint,
            "connected": self.connected,
            "total_jobs": len(jobs),
            "completed": sum(1 for j in jobs if j.status == "completed"),
            "failed": sum(1 for j in jobs if j.status == "failed"),
        }


# ---------------------------------------------------------------------------
# Hugging Face Model Registry
# ---------------------------------------------------------------------------

@dataclass
class HuggingFaceModel:
    """Metadata for a Hugging Face model used by ESPiritAi."""

    model_id: str           # e.g. "google/flan-t5-base"
    task: str               # e.g. "text-generation", "text-classification"
    description: str = ""
    loaded: bool = False
    last_used: Optional[float] = None


class HuggingFaceClient:
    """
    Manages integration with Hugging Face models for AI enhancement.

    The client maintains a registry of models used by ESPiritAi and
    provides a ``run`` method that dispatches inference calls.  When
    the ``transformers`` library is available the client uses the real
    pipeline; otherwise it falls back to a deterministic stub so the
    system operates without heavy ML dependencies.
    """

    # Curated model registry for ESPx / ESPiritAi use cases
    DEFAULT_MODELS: Dict[str, HuggingFaceModel] = {
        "code-gen": HuggingFaceModel(
            model_id="Salesforce/codegen-350M-mono",
            task="text-generation",
            description="Code generation for firmware snippets.",
        ),
        "nlp-qa": HuggingFaceModel(
            model_id="deepset/roberta-base-squad2",
            task="question-answering",
            description="Q&A over ESP documentation.",
        ),
        "sentiment": HuggingFaceModel(
            model_id="distilbert-base-uncased-finetuned-sst-2-english",
            task="text-classification",
            description="Classify user feedback / telemetry alerts.",
        ),
        "embedding": HuggingFaceModel(
            model_id="sentence-transformers/all-MiniLM-L6-v2",
            task="feature-extraction",
            description="Semantic embeddings for knowledge retrieval.",
        ),
        "anomaly": HuggingFaceModel(
            model_id="huggingface/autorain",
            task="text-classification",
            description="Anomaly detection in log streams.",
        ),
    }

    def __init__(self, use_stubs: bool = True) -> None:
        """
        Parameters
        ----------
        use_stubs:
            When True (default) the client uses deterministic stubs for
            all inference calls so that no internet connection or GPU is
            required.  Set to False to attempt real Hugging Face inference
            via the ``transformers`` library.
        """
        self._registry: Dict[str, HuggingFaceModel] = dict(self.DEFAULT_MODELS)
        self._use_stubs = use_stubs
        self._pipelines: Dict[str, Any] = {}  # model_alias -> pipeline obj

    # -- Registry management -----------------------------------------------

    def register_model(self, alias: str, model: HuggingFaceModel) -> None:
        self._registry[alias] = model

    def list_models(self) -> List[Dict[str, Any]]:
        return [
            {
                "alias": alias,
                "model_id": m.model_id,
                "task": m.task,
                "loaded": m.loaded,
            }
            for alias, m in self._registry.items()
        ]

    # -- Inference ---------------------------------------------------------

    def run(
        self,
        model_alias: str,
        inputs: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Run inference with the specified model.

        Returns a result dict with at least a ``output`` key.
        """
        model = self._registry.get(model_alias)
        if model is None:
            return {"error": f"Model alias '{model_alias}' not registered."}

        if self._use_stubs:
            return self._stub_inference(model, inputs)

        # Attempt real transformers pipeline (optional dependency)
        return self._real_inference(model_alias, model, inputs, **kwargs)

    def _stub_inference(
        self, model: HuggingFaceModel, inputs: Any
    ) -> Dict[str, Any]:
        """
        Deterministic stub inference — returns a plausible-shaped response
        without any actual model weights.
        """
        seed = int(hashlib.md5(str(inputs).encode()).hexdigest(), 16) % 10_000
        model.last_used = time.time()
        model.loaded = True

        if model.task == "text-generation":
            return {
                "output": f"// stub codegen [{seed}]: void setup(){{ /* {inputs} */ }}",
                "model": model.model_id,
                "stub": True,
            }
        if model.task == "question-answering":
            return {
                "output": {"answer": f"stub_answer_{seed}", "score": 0.75},
                "model": model.model_id,
                "stub": True,
            }
        if model.task == "text-classification":
            label = "POSITIVE" if seed % 2 == 0 else "NEGATIVE"
            return {
                "output": [{"label": label, "score": 0.8 + (seed % 20) / 100}],
                "model": model.model_id,
                "stub": True,
            }
        if model.task == "feature-extraction":
            # Return a fake 384-dim embedding
            import random as _r
            _r.seed(seed)
            embedding = [_r.gauss(0, 1) for _ in range(384)]
            return {"output": embedding, "model": model.model_id, "stub": True}
        return {"output": None, "model": model.model_id, "stub": True}

    def _real_inference(
        self,
        alias: str,
        model: HuggingFaceModel,
        inputs: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        try:
            from transformers import pipeline  # type: ignore

            if alias not in self._pipelines:
                self._pipelines[alias] = pipeline(model.task, model=model.model_id)
                model.loaded = True

            result = self._pipelines[alias](inputs, **kwargs)
            model.last_used = time.time()
            return {"output": result, "model": model.model_id, "stub": False}
        except ImportError:
            return self._stub_inference(model, inputs)
        except Exception as exc:  # pylint: disable=broad-except
            return {"error": str(exc), "model": model.model_id}

    # -- Metrics -----------------------------------------------------------

    def metrics(self) -> Dict[str, Any]:
        return {
            "registered_models": len(self._registry),
            "loaded_models": sum(1 for m in self._registry.values() if m.loaded),
            "use_stubs": self._use_stubs,
        }


# ---------------------------------------------------------------------------
# Distributed Processor
# ---------------------------------------------------------------------------

class DistributedProcessor:
    """
    Coordinates distributed processing across the cloud compute client
    and Hugging Face models to serve ESPiritAi's compute needs.
    """

    def __init__(
        self,
        cloud: Optional[CloudComputeClient] = None,
        hf: Optional[HuggingFaceClient] = None,
    ) -> None:
        self.cloud = cloud or CloudComputeClient()
        self.hf = hf or HuggingFaceClient(use_stubs=True)
        self._dispatch_log: List[Dict[str, Any]] = []

    def process(
        self,
        request_type: str,
        payload: Dict[str, Any],
        model_alias: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Route a processing request to the appropriate backend.

        ``request_type`` starting with ``"hf_"`` is routed to Hugging Face;
        everything else goes to cloud compute.
        """
        t0 = time.time()
        if request_type.startswith("hf_"):
            alias = model_alias or request_type[3:]
            result = self.hf.run(alias, payload.get("input", payload))
            backend = "huggingface"
        else:
            job = self.cloud.submit(request_type, payload)
            result = job.result or {}
            backend = "cloud"

        entry = {
            "request_type": request_type,
            "backend": backend,
            "latency_s": round(time.time() - t0, 4),
            "success": "error" not in result,
        }
        self._dispatch_log.append(entry)
        return result

    def metrics(self) -> Dict[str, Any]:
        total = len(self._dispatch_log)
        success = sum(1 for e in self._dispatch_log if e["success"])
        return {
            "total_requests": total,
            "success_rate": round(success / total, 4) if total else 0.0,
            "cloud": self.cloud.metrics(),
            "huggingface": self.hf.metrics(),
        }
