import os
import sys

# Configuration
class Config:
    def __init__(self):
        # Check for different API key environment variables
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.ark_api_key = os.environ.get("ARK_API_KEY")
        
        # Use ARK_API_KEY if available and base_url is ARK, otherwise use OPENAI_API_KEY
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        if "ark-cn-beijing.bytedance.net" in base_url and self.ark_api_key:
            self.api_key = self.ark_api_key
        elif self.openai_api_key:
            self.api_key = self.openai_api_key
        else:
            raise ValueError("No valid API key found. Set either OPENAI_API_KEY or ARK_API_KEY")
        
        # Add Anthropic API key for client validation
        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.anthropic_api_key:
            print("Warning: ANTHROPIC_API_KEY not set. Client API key validation will be disabled.")
        
        self.openai_base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.azure_api_version = os.environ.get("AZURE_API_VERSION")  # For Azure OpenAI
        self.host = os.environ.get("HOST", "0.0.0.0")
        self.port = int(os.environ.get("PORT", "8082"))
        self.log_level = os.environ.get("LOG_LEVEL", "INFO")
        self.max_tokens_limit = int(os.environ.get("MAX_TOKENS_LIMIT", "4096"))
        self.min_tokens_limit = int(os.environ.get("MIN_TOKENS_LIMIT", "100"))
        
        # Connection settings
        self.request_timeout = int(os.environ.get("REQUEST_TIMEOUT", "90"))
        self.max_retries = int(os.environ.get("MAX_RETRIES", "2"))
        
        # Model settings - BIG and SMALL models
        self.big_model = os.environ.get("BIG_MODEL", "gpt-4o")
        self.middle_model = os.environ.get("MIDDLE_MODEL", self.big_model)
        self.small_model = os.environ.get("SMALL_MODEL", "gpt-4o-mini")
        
        # Multi-API-Key to model mapping
        self.api_key_model_mapping = self._load_api_key_model_mapping()
        
    def _load_api_key_model_mapping(self):
        """
        Load API key to model mapping from environment variables.
        
        Environment variables format:
        API_KEY_MODEL_MAPPING_<KEY_ID>_BIG="model-name"
        API_KEY_MODEL_MAPPING_<KEY_ID>_MIDDLE="model-name"  
        API_KEY_MODEL_MAPPING_<KEY_ID>_SMALL="model-name"
        API_KEY_MODEL_MAPPING_<KEY_ID>_API_KEY="actual-api-key"
        
        Returns a dict mapping API keys to model configurations.
        """
        mapping = {}
        
        # Find all mapping configurations
        for key, value in os.environ.items():
            if key.startswith("API_KEY_MODEL_MAPPING_") and key.endswith("_API_KEY"):
                # Extract the key ID
                key_id = key.replace("API_KEY_MODEL_MAPPING_", "").replace("_API_KEY", "")
                api_key = value
                
                # Get corresponding model configurations
                big_model = os.environ.get(f"API_KEY_MODEL_MAPPING_{key_id}_BIG", self.big_model)
                middle_model = os.environ.get(f"API_KEY_MODEL_MAPPING_{key_id}_MIDDLE", big_model)
                small_model = os.environ.get(f"API_KEY_MODEL_MAPPING_{key_id}_SMALL", self.small_model)
                
                # Get ignore temperature setting for this API key
                ignore_temperature = os.environ.get(f"API_KEY_MODEL_MAPPING_{key_id}_IGNORE_TEMPERATURE", "")
                
                mapping[api_key] = {
                    "big_model": big_model,
                    "middle_model": middle_model,
                    "small_model": small_model,
                    "ignore_temperature": ignore_temperature.lower() in ["true", "1"]
                }
        
        return mapping
    
    def get_models_for_api_key(self, api_key):
        """Get model configuration for a specific API key."""
        if api_key in self.api_key_model_mapping:
            return self.api_key_model_mapping[api_key]
        
        # Fallback to default models
        default_ignore_temp = os.environ.get("MODEL_IGNORE_TEMPERATURE", "").lower() in ["true", "1"]
        return {
            "big_model": self.big_model,
            "middle_model": self.middle_model,
            "small_model": self.small_model,
            "ignore_temperature": default_ignore_temp
        }
        
    def validate_api_key(self):
        """Basic API key validation"""
        if not self.api_key:
            print("api key validate fail, not set.")
            return False
        
        # Skip format validation for ARK API or ByteDance API
        if "ark-cn-beijing.bytedance.net" in self.openai_base_url or "bytedance.net" in self.openai_base_url:
            print("api key validate pass!")
            return True
            
        # Basic format check for OpenAI API keys
        if not self.api_key.startswith('sk-'):
            print("api key validate fail!")
            return False
        return True
        
    def validate_client_api_key(self, client_api_key):
        """Validate client's Anthropic API key"""
        # If no ANTHROPIC_API_KEY is set in the environment, skip validation
        if not self.anthropic_api_key and not self.api_key_model_mapping:
            return True
            
        # Check if the client's API key matches the expected value (legacy single-key mode)
        if self.anthropic_api_key and client_api_key == self.anthropic_api_key:
            return True
            
        # Check if the client's API key is in the multi-key mapping
        if client_api_key in self.api_key_model_mapping:
            return True
            
        return False

try:
    config = Config()
    print(f" Configuration loaded: API_KEY={'*' * 20}..., BASE_URL='{config.openai_base_url}'")
except Exception as e:
    print(f"=4 Configuration Error: {e}")
    sys.exit(1)
