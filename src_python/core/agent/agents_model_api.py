import requests
import google.generativeai as genai
from anthropic import Anthropic
from abc import ABC, abstractmethod

from .agents_base import BaseAgent
from ..models.observation_model import ObservationModel

class RestAgent(BaseAgent, ABC):
    """
    Abstract base class for REST API-based agents using the OpenAI-style chat schema.

    Supports GPT, Mistral, and Grok via shared transport and message structure.
    """

    @property
    @abstractmethod
    def api_url(self) -> str:
        """
        The full URL of the REST API endpoint.
        Subclasses must implement this as a property.
        """
        pass

    @property
    @abstractmethod
    def api_key(self) -> str:
        """
        The full URL of the REST API endpoint.
        Subclasses must implement this as a property.
        """
        pass

    def act(self, observation: ObservationModel) -> str:
        messages = [
            {"role": "system", "content": observation.system_prompt},
            {"role": "user", "content": observation.user_prompt}
        ]

        payload = {
            "model": self.model_type,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            response = requests.post(
                url=self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.RequestException as e:
            raise RuntimeError(f"{self.model_type.upper()} API request failed: {e}")

# -------------------------------#
#           GPT BaseAgent            #
# -------------------------------#
@BaseAgent.register_subclass("gpt")
class GPTAgent(RestAgent):

    @property
    def api_url(self) -> str:
        return "https://api.openai.com/v1/chat/completions"

    @property
    def api_key(self) -> str:
        return self.api_keys["GPT_API_KEY"]

# -------------------------------#
#           Mistral BaseAgent        #
# -------------------------------#
@BaseAgent.register_subclass("mistral")
class MistralAgent(BaseAgent):

    @property
    def api_url(self) -> str:
        return "https://api.mistral.ai/v1/chat/completions"

    @property
    def api_key(self) -> str:
        return self.api_keys["MISTRAL_API_KEY"]

# -------------------------------#
#           Grok BaseAgent           #
# -------------------------------#
@BaseAgent.register_subclass("grok")
class GrokAgent(BaseAgent):

    @property
    def api_url(self) -> str:
        return "https://api.x.ai/v1/chat/completions"

    @property
    def api_key(self) -> str:
        return self.api_keys["GROK_API_KEY"]

# -------------------------------#
#           Claude BaseAgent         #
# -------------------------------#
@BaseAgent.register_subclass("claude")
class ClaudeAgent(BaseAgent):

    def __init__(self, agent_params):
        super().__init__(agent_params)
        self.client = Anthropic(api_key=self.api_key)

    @property
    def api_key(self) -> str:
        return self.api_keys["CLAUDE_API_KEY"]

    def act(self, observation: ObservationModel) -> str:
        """
        Constructs a multimodal prompt and sends it to the Claude API (Anthropic SDK).

        Args:
            observation (ObservationModel): The current environment state, including images and history.

        Returns:
            str: The model's text response.
        """
        messages = [
            {"role": "user", "content": [{"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": observation.prev_image_base64}}]},
            {"role": "assistant", "content": f"Action: {observation.prev_exchange['response']}"},
            {"role": "user", "content": [{"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": observation.goal_base64}}]},
            {"role": "user", "content": [{"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": observation.current_base64}}]},
            {"role": "user", "content": observation.user_prompt}
        ]

        try:
            message = self.client.messages.create(
                model=self.model_type,
                max_tokens=500,
                temperature=0.5,
                system=observation.system_prompt,
                messages=messages
            )
            return message.content[0].text
        except Exception as e:
            raise RuntimeError(f"Claude API call failed: {e}")


# -------------------------------#
#           Gemini BaseAgent         #
# -------------------------------#
@BaseAgent.register_subclass("gemini")
class GeminiAgent(BaseAgent):

    def __init__(self, agent_params):
        super().__init__(agent_params)
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            model_name=f"models/{self.model_type}",
            system_instruction=self.system_prompt
        )

    @property
    def api_key(self) -> str:
        return self.api_keys["GEMINI_API_KEY"]

    def act(self, observation: ObservationModel) -> str:
        """
        Constructs a multimodal prompt and sends it to the Gemini API via the google.generativeai SDK.

        Args:
            observation (ObservationModel): The current environment state, including prompt and base64 images.

        Returns:
            str: The model's text response.
        """
        messages = [
            {"mime_type": "image/png", "data": observation.goal_base64},
            {"mime_type": "image/png", "data": observation.current_base64},
            observation.user_prompt
        ]

        try:
            response = self.model.generate_content(
                messages,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini API call failed: {e}")
