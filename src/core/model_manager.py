from src.core.config import config
from src.core.context import get_current_api_key
import logging

logger = logging.getLogger(__name__)

class ModelManager:
    def __init__(self, config):
        self.config = config
    
    def map_claude_model_to_openai(self, claude_model: str) -> str:
        """Map Claude model names to OpenAI model names based on BIG/SMALL pattern"""
        # If it's already an OpenAI model, return as-is
        if claude_model.startswith("gpt-") or claude_model.startswith("o1-"):
            return claude_model

        # If it's other supported models (ARK/Doubao/DeepSeek), return as-is
        if (claude_model.startswith("ep-") or claude_model.startswith("doubao-") or 
            claude_model.startswith("deepseek-")):
            return claude_model
        
        # Get model configuration based on current API key
        current_api_key = get_current_api_key()
        models_config = self.config.get_models_for_api_key(current_api_key)
        
        # Map based on model naming patterns
        model_lower = claude_model.lower()
        mapped_model = None
        model_type = None
        
        if 'haiku' in model_lower:
            mapped_model = models_config["small_model"]
            model_type = "SMALL"
        elif 'sonnet' in model_lower:
            mapped_model = models_config["middle_model"]
            model_type = "MIDDLE"
        elif 'opus' in model_lower:
            mapped_model = models_config["big_model"]
            model_type = "BIG"
        else:
            # Default to big model for unknown models
            mapped_model = models_config["big_model"]
            model_type = "BIG(default)"
        
        # Log the model mapping
        masked_key = "****"
        if current_api_key:
            masked_key = f"{current_api_key[:8]}...{current_api_key[-4:]}" if len(current_api_key) > 12 else "****"
        
        logger.info(f"Model mapping: {claude_model} -> {mapped_model} (type: {model_type}, API: {masked_key})")
        
        return mapped_model

model_manager = ModelManager(config)