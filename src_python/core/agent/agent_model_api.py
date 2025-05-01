import requests

from .agent import Agent
from ..utility.json_file_handler import JsonFileHandler


@Agent.register_subclass("model")
class APIModelAgent(Agent):

    def __init__(self, agent_params):
        super().__init__(agent_params)
        self.model_type = agent_params.get("model_type", None)
        self.model = agent_params.get("model_type", "gpt-4o")
        self.api_key = JsonFileHandler.load_json(file_signature="api-keys", source_dir="api-keys")[self.model_type]
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.max_tokens = 500 #Load from params later
        if not self.api_key:
            raise ValueError("Missing GPT4_API_KEY in API key file")

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def act(self, observation):
        """
        Constructs a multimodal prompt and sends it to the GPT-4 API.

        Args:
            observation (ObservationModel): Contains system prompt, user prompt, and base64 screenshots.

        Returns:
            str: Raw text response from the model.
        """
        payload = {
            "model": self.model,
            "messages": self._build_messages(observation),
            "max_tokens": self.max_tokens
        }

        try:
            response = requests.post(
                url=self.api_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

        except requests.RequestException as e:
            raise RuntimeError(f"API request failed: {e}")

    def _build_messages(self, observation):
        raise NotImplementedError("Subclasses must implement _build_messages")

    def _parse_response(self, json_response):
        raise NotImplementedError("Subclasses must implement _build_messages")

@Agent.register_subclass("openai_gpt")
class GPTAgent(APIModelAgent):

    def __init__(self, agent_params):
        super().__init__(agent_params)

    def _parse_response(self, json_response):
        """ Default OpenAI-style parsing. Override if needed. """
        return json_response["choices"][0]["message"]["content"]

    def _build_messages(self, obs) -> list:
        """
        Constructs the full list of messages for the OpenAI chat API.
        """
        return [
            {"role": "system", "content": obs.system_prompt},
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{obs.goal_base64}"}}]},
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{obs.current_base64}"}}]},
            {"role": "user", "content": obs.user_prompt}
        ]