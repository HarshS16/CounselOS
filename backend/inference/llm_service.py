import json
import logging
import threading
from pathlib import Path

from backend.config import settings

logger = logging.getLogger(__name__)


class LLMError(Exception):
    pass


class ModelNotFoundError(LLMError):
    pass


class ModelLoadError(LLMError):
    pass


class LLMService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> "LLMService":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._model = None
        self._model_path: str = settings.llm_model_path
        self._context_length: int = settings.llm_context_length
        self._default_max_tokens: int = settings.llm_max_tokens
        self._default_temperature: float = settings.llm_temperature
        self._n_gpu_layers: int = settings.llm_n_gpu_layers
        self._n_threads: int = settings.llm_n_threads
        self._initialized = True

    def _load_model(self) -> None:
        if self._model is not None:
            return

        model_path = Path(self._model_path)
        if not self._model_path or not model_path.exists():
            raise ModelNotFoundError(
                f"Model file not found: {self._model_path}. "
                "Set COUNSELOS_LLM_MODEL_PATH to a valid .gguf file."
            )

        try:
            from llama_cpp import Llama

            self._model = Llama(
                model_path=str(model_path),
                n_ctx=self._context_length,
                n_gpu_layers=self._n_gpu_layers,
                n_threads=self._n_threads,
                verbose=settings.debug,
            )
            logger.info("Model loaded: %s (ctx=%d)", model_path.name, self._context_length)
        except ImportError:
            raise ModelLoadError(
                "llama-cpp-python is not installed. Install it with: "
                "pip install llama-cpp-python"
            )
        except MemoryError:
            self._model = None
            raise ModelLoadError(
                "Insufficient memory to load the model. "
                "Try a smaller quantization or reduce context length."
            )
        except Exception as exc:
            self._model = None
            raise ModelLoadError(f"Failed to load model: {exc}") from exc

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    @property
    def model_info(self) -> dict:
        return {
            "model_path": self._model_path,
            "context_length": self._context_length,
            "max_tokens": self._default_max_tokens,
            "temperature": self._default_temperature,
            "n_gpu_layers": self._n_gpu_layers,
            "n_threads": self._n_threads,
            "loaded": self.is_loaded,
        }

    def generate(
        self,
        prompt: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
        stop: list[str] | None = None,
    ) -> str:
        self._load_model()

        max_tokens = max_tokens or self._default_max_tokens
        temperature = temperature if temperature is not None else self._default_temperature

        try:
            result = self._model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=stop or [],
                echo=False,
            )
            text = result["choices"][0]["text"].strip()
            return text
        except Exception as exc:
            logger.error("Generation failed: %s", exc)
            raise LLMError(f"Generation failed: {exc}") from exc

    def generate_structured(
        self,
        prompt: str,
        schema: dict | None = None,
        max_tokens: int | None = None,
    ) -> dict:
        max_retries = 2
        last_error: Exception | None = None

        for attempt in range(max_retries + 1):
            raw = self.generate(
                prompt,
                max_tokens=max_tokens,
                stop=["\n\n\n"],
            )

            json_str = _extract_json(raw)
            if json_str is None:
                last_error = ValueError(f"No JSON found in model output (attempt {attempt + 1})")
                logger.warning("Structured generation attempt %d: no JSON found", attempt + 1)
                continue

            try:
                parsed = json.loads(json_str)
                return parsed
            except json.JSONDecodeError as exc:
                last_error = exc
                logger.warning(
                    "Structured generation attempt %d: JSON parse error: %s",
                    attempt + 1,
                    exc,
                )
                continue

        raise LLMError(f"Failed to generate valid JSON after {max_retries + 1} attempts: {last_error}")

    def unload(self) -> None:
        self._model = None
        logger.info("Model unloaded")


def _extract_json(text: str) -> str | None:
    for start_char, end_char in [("{", "}"), ("[", "]")]:
        start = text.find(start_char)
        if start == -1:
            continue
        depth = 0
        in_string = False
        escape_next = False
        for i in range(start, len(text)):
            c = text[i]
            if escape_next:
                escape_next = False
                continue
            if c == "\\":
                escape_next = True
                continue
            if c == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if c == start_char:
                depth += 1
            elif c == end_char:
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]
    return None
