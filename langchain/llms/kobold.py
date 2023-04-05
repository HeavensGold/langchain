"""Wrapper around KoboldAI APIs."""
from typing import Any, Dict, List, Mapping, Optional

import requests
from pydantic import BaseModel, Extra, root_validator

from langchain.llms.base import LLM
from langchain.llms.utils import enforce_stop_tokens
from langchain.utils import get_from_dict_or_env


class KoboldAI(LLM, BaseModel):
    """Wrapper around KoboldAI large language models.

    Example:
        .. code-block:: python

            from langchain.llms import KoboldAI
            koboldai = KoboldAI()
    """

    temperature: float = 1.99
    """What sampling temperature to use."""

    length: int = 256
    """The maximum number of tokens to generate in the completion."""

    top_p: float = 0.18
    """Total probability mass of tokens to consider at each step."""

    typical_p: float = 1.0

    top_k: int = 30
    """The number of highest probability vocabulary tokens to
    keep for top-k-filtering."""

    repetition_penalty: int = 1.15
    """Penalizes repeated tokens according to frequency."""

    url: str = "http://127.0.0.1:5000/api/v1/generate"
    """Base url"""

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        #validate urls
        return values

    @property
    def _default_params(self) -> Mapping[str, Any]:
        """Get the default parameters for calling KoboldAI API."""
        return {
            "temperature": self.temperature,
            "max_length": self.length,
            "top_p": self.top_p,
            "typical": self.typical_p,
            "top_k": self.top_k,
            "rep_pen": self.repetition_penalty,
        }

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {**{"url": self.url}, **self._default_params}

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "koboldai"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Call out to KoboldAI's complete endpoint.

        Args:
            prompt: The prompt to pass into the model.
            stop: Optional list of stop words to use when generating.

        Returns:
            The string generated by the model.

        Example:
            .. code-block:: python

                response = KoboldAI("Tell me a joke.")
        """
        response = requests.post(
            url=self.url,
            headers={
                "Content-Type": "application/json",
            },
            json={"prompt": prompt, **self._default_params},
        )
        response_json = response.json()
        text = response_json["results"][0]["text"]
        if stop is not None:
            # I believe this is required since the stop tokens
            # are not enforced by the model parameters
            text = enforce_stop_tokens(text, stop)
        return text
