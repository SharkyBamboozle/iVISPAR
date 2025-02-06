import agent_systems
import game_systems
import experiment_utilities as util

def init_env(env_params, episode_path=None, episode_logger=None):
    config = util.expand_config_file(
        experiment_path=episode_path,
        grid_label=env_params.get('grid_label', None),
        camera_offset=env_params.get('camera_offset', None),
        camera_auto_override=env_params.get('camera_auto_override', None),
        screenshot_alpha=env_params.get('screenshot_alpha', None),
        auto_done_check=env_params.get('auto_done_check', None)
    )
    return config

def init_agent(agent_params, episode_path, config, episode_logger):
    # Initialise agent
    if agent_params.get('agent_type', {}) == 'AIAgent':
        move_set = agent_params.get('move_set', None)
        agent = agent_systems.AIAgent(
            episode_logger,
            config.get(move_set, [])
        )
    elif agent_params.get('agent_type', {}) == 'UserAgent':
        agent = agent_systems.UserAgent()
    elif agent_params.get('agent_type', {}) == 'GPT4Agent':
        agent = agent_systems.GPT4Agent(
            episode_path=episode_path,
            episode_logger=episode_logger,
            api_key_file_path=agent_params.get('api_keys_file_path', None),
            instruction_prompt_file_path=agent_params.get('instruction_prompt_file_path', None),
            visual_state_embedding=agent_params.get('visual_state_embedding', None),
            single_images=agent_params.get('single_images', True),
            COT=agent_params.get('COT', False),
            delay=agent_params.get('delay', 0),
            max_history = agent_params.get('max_history', 0)
        )
    elif agent_params.get('agent_type', {}) == 'ClaudeAgent':
        agent = agent_systems.ClaudeAgent(
            episode_path=episode_path,
            episode_logger=episode_logger,
            api_key_file_path=agent_params.get('api_keys_file_path', None),
            instruction_prompt_file_path=agent_params.get('instruction_prompt_file_path', None),
            visual_state_embedding=agent_params.get('visual_state_embedding', None),
            single_images=agent_params.get('single_images', True),
            COT=agent_params.get('COT', False),
            delay=agent_params.get('delay', 0),
            max_history = agent_params.get('max_history', 0)
        )
    elif agent_params.get('agent_type', {}) == 'Qwen2VLAgent':
        agent = agent_systems.Qwen2VLAgent(
            model_path=agent_params.get('model_path', None),
            instruction_prompt_file_path=agent_params.get('instruction_prompt_file_path', None),
            max_history = agent_params.get('max_history', 0),
            visual_state_embedding=agent_params.get('visual_state_embedding', None),
            n_gpus=agent_params.get('n_gpus', None),
            COT=agent_params.get('COT', False)
        )
    elif agent_params.get('agent_type', {}) == 'LlamaAgent':
        agent = agent_systems.LlamaAgent(
            model_path=agent_params.get('model_path', None),
            instruction_prompt_file_path=agent_params.get('instruction_prompt_file_path', None),
            max_history = agent_params.get('max_history', 0),
            visual_state_embedding=agent_params.get('visual_state_embedding', None),
            n_gpus=agent_params.get('n_gpus', None),
            COT=agent_params.get('COT', False)
        )
    elif agent_params.get('agent_type', {}) == 'InternVLAgent':
        agent = agent_systems.InternVLAgent(
            model_path=agent_params.get('model_path', None),
            instruction_prompt_file_path=agent_params.get('instruction_prompt_file_path', None),
            visual_state_embedding=agent_params.get('visual_state_embedding', None),
            n_gpus=agent_params.get('n_gpus', None),
            COT=agent_params.get('COT', False),
            max_history = agent_params.get('max_history', 0)
        )
    elif agent_params.get('agent_type', {}) == 'LLaVaOneVisionAgent':
        agent = agent_systems.LLaVaOneVisionAgent(
            model_path=agent_params.get('model_path', None),
            instruction_prompt_file_path=agent_params.get('instruction_prompt_file_path', None),
            visual_state_embedding=agent_params.get('visual_state_embedding', None),
            n_gpus=agent_params.get('n_gpus', None),
            COT=agent_params.get('COT', False),
            max_history = agent_params.get('max_history', 0)
        )
    elif agent_params.get('agent_type', {}) == 'DeepseekAgent':
        agent = agent_systems.DeepseekAgent(
            model_path=agent_params.get('model_path', None),
            instruction_prompt_file_path=agent_params.get('instruction_prompt_file_path', None),
            visual_state_embedding=agent_params.get('visual_state_embedding', None),
            n_gpus=agent_params.get('n_gpus', None),
            COT=agent_params.get('COT', False),
            max_history = agent_params.get('max_history', 0)
        )
    elif agent_params.get('agent_type', {}) == 'GeminiAgent':
        agent = agent_systems.GeminiAgent(
            episode_path=episode_path,
            episode_logger=episode_logger,
            api_key_file_path=agent_params.get('api_keys_file_path', None),
            instruction_prompt_file_path=agent_params.get('instruction_prompt_file_path', None),
            visual_state_embedding=agent_params.get('visual_state_embedding', None),
            single_images=agent_params.get('single_images', True),
            COT=agent_params.get('COT', False),
            delay=agent_params.get('delay', 0),
            max_history = agent_params.get('max_history', 0)
        )
    else:
        raise ValueError(f"Unsupported agent_type: {agent_params.get('agent_type', {})}")
    return agent

def init_game(game_params, episode_path, episode_logger):
    # Initialise game
    if game_params.get('game_type', {}) == 'InteractivePuzzle':
        game = game_systems.InteractivePuzzle(
            experiment_id=episode_path,
            instruction_prompt_file_path=game_params.get("instruction_prompt_file_path", None),
            chain_of_thoughts=game_params.get("chain_of_thoughts", None),
            representation_type=game_params.get("representation_type", None),
            planning_steps=game_params.get("planning_steps", None),
            max_game_length=game_params.get('max_game_length', None),
            predict_board_state=game_params.get('predict_board_state', False),
        )
    elif game_params.get('game_type', {}) == 'SceneUnderstanding':
        game = game_systems.SceneUnderstanding(
            experiment_id=episode_path,
            instruction_prompt_file_path=game_params.get("instruction_prompt_file_path", None),
            chain_of_thoughts=game_params.get("chain_of_thoughts", None),
        )
    else:
        raise ValueError(f"Unsupported game_type: {game_params.get('game_type', {})}")
    return game
