from abc import ABC, abstractmethod
from typing import Type, Callable, Dict, Any

from vllm import LLM, SamplingParams

from .agents_base import BaseAgent
from ..models.observation_model import ObservationModel

class LocalAgent(BaseAgent, ABC):
    """
    Abstract base class for local agents that load and run models with image + text prompts.
    """

    def __init__(self, agent_params: Dict[str, Any]):
        super().__init__(agent_params)

        self.model_path = agent_params["model_path"]
        self.max_history = agent_params.get("max_history", 2)
        self.visual_state_embedding = agent_params.get("visual_state_embedding", "both")
        self.temperature = agent_params.get("temperature", 1.0)
        self.n_gpus = agent_params.get("n_gpus", 1)
        self.model = self._load_model()

        self.stop_token_ids = None  # optionally overridden

    def _load_model(self):
        return LLM(
            self.model_path,
            tensor_parallel_size=self.n_gpus,
            enforce_eager=self.n_gpus > 4,
            limit_mm_per_prompt={"image": self.max_history + 2},
            trust_remote_code=True
        )

    @abstractmethod
    def build_prompt(self, observation: ObservationModel) -> tuple[str, list]:
        """
        Build a prompt string and list of image objects from an observation.

        Returns:
            Tuple of (prompt, image_data) to feed into the model.
        """
        pass

    def act(self, observation: ObservationModel) -> str:
        prompt, image_data = self.build_prompt(observation)

        sampling_params = SamplingParams(
            temperature=self.temperature,
            top_p=0.95,
            top_k=50,
            max_tokens=self.max_tokens,
            stop_token_ids=self.stop_token_ids
        )

        try:
            response = self.model.generate(
                {
                    "prompt": prompt,
                    "multi_modal_data": {"image": image_data}
                },
                sampling_params=sampling_params
            )
            return response[0].outputs[0].text
        except Exception as e:
            raise RuntimeError(f"Local model generation failed: {e}")


@BaseAgent.register_subclass("qwen")
class QwenAgent(LocalAgent):
    def __init__(self, agent_params):
        super().__init__(agent_params)
        self.processor = AutoProcessor.from_pretrained(self.model_path)

    def build_prompt(self, observation):
        formatted = observation.to_qwen_format()
        prompt = self.processor.apply_chat_template(formatted, tokenize=False, add_generation_prompt=True)
        image_data, _ = process_vision_info(formatted)
        return prompt.strip(), image_data or []


@BaseAgent.register_subclass("llava")
class LLaVaAgent(LocalAgent):
    def build_prompt(self, observation):
        conv = observation.to_llava_conversation_template()
        return conv.get_prompt().strip(), observation.get_images()


@BaseAgent.register_subclass("llama")
class LlamaAgent(LocalAgent):
    def __init__(self, agent_params):
        super().__init__(agent_params)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)

    def build_prompt(self, observation: ObservationModel) -> tuple[str, list]:
        formatted = observation.to_llama_chat_format()
        prompt = self.tokenizer.apply_chat_template(formatted, add_generation_prompt=True, tokenize=False)
        return prompt.strip(), observation.get_images()


@BaseAgent.register_subclass("deepseek")
class DeepseekAgent(LocalAgent):
    def __init__(self, agent_params):
        super().__init__(agent_params)
        self.model = LLM(
            self.model_path,
            tensor_parallel_size=self.n_gpus,
            enforce_eager=self.n_gpus > 4,
            limit_mm_per_prompt={"image": self.max_history + 2},
            hf_overrides={"architectures": ["DeepseekVLV2ForCausalLM"]},
            trust_remote_code=True
        )

    def build_prompt(self, observation: ObservationModel) -> tuple[str, list]:
        prompt = observation.to_deepseek_format()
        return prompt.strip(), observation.get_images()


@BaseAgent.register_subclass("internvl")
class InternVLAgent(LocalAgent):
    def __init__(self, agent_params):
        super().__init__(agent_params)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)

        stop_tokens = ["<|endoftext|>", "<|im_start|>", "<|im_end|>", "<|end|>"]
        self.stop_token_ids = [self.tokenizer.convert_tokens_to_ids(t) for t in stop_tokens]

    def build_prompt(self, observation: ObservationModel) -> tuple[str, list]:
        formatted = observation.to_internvl_format()
        prompt = self.tokenizer.apply_chat_template(formatted, tokenize=False, add_generation_prompt=True)
        return prompt.strip(), observation.get_images()
