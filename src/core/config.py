import json
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

        # Streaming mode settings
        self.default_streaming_mode = self._load_default_streaming_mode()
        self.model_streaming_modes = self._load_model_streaming_modes()
        
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

    def _load_default_streaming_mode(self) -> str:
        mode = os.environ.get("DEFAULT_STREAMING_MODE", "stream").strip().lower()
        if mode not in {"stream", "buffered"}:
            print(f"Warning: DEFAULT_STREAMING_MODE='{mode}' is invalid. Falling back to 'stream'.")
            return "stream"
        return mode

    def _load_model_streaming_modes(self) -> dict:
        """Load per-model streaming mode overrides."""
        overrides = {}

        raw_mapping = os.environ.get("MODEL_STREAMING_MODES")
        if raw_mapping:
            try:
                data = json.loads(raw_mapping)
                if isinstance(data, dict):
                    for model_name, mode in data.items():
                        normalized_mode = str(mode).strip().lower()
                        if normalized_mode in {"stream", "buffered"}:
                            overrides[model_name.lower()] = normalized_mode
                        else:
                            print(
                                f"Warning: Streaming mode '{mode}' for model '{model_name}' is invalid. Expected 'stream' or 'buffered'."
                            )
                else:
                    print("Warning: MODEL_STREAMING_MODES must be a JSON object mapping model names to modes.")
            except json.JSONDecodeError as exc:
                print(f"Warning: Failed to parse MODEL_STREAMING_MODES as JSON: {exc}")

        prefix = "STREAMING_MODE_"
        for key, value in os.environ.items():
            if not key.startswith(prefix):
                continue

            token = key[len(prefix):]
            model_name = self._env_token_to_model_name(token)
            normalized_mode = str(value).strip().lower()

            if normalized_mode not in {"stream", "buffered"}:
                print(
                    f"Warning: Streaming mode override '{value}' for env '{key}' is invalid. Expected 'stream' or 'buffered'."
                )
                continue

            overrides[model_name.lower()] = normalized_mode

        if overrides:
            print(
                f"Streaming mode overrides loaded (default='{self.default_streaming_mode}'): "
                + ", ".join(f"{model}={mode}" for model, mode in overrides.items())
            )

        return overrides

    def _env_token_to_model_name(self, token: str) -> str:
        """Convert STREAMING_MODE_* env token to model name.

        Follows convention: replace double underscores with slashes, single underscores with hyphens.
        """
        normalized = token.strip()
        normalized = normalized.replace("__", "/")
        normalized = normalized.replace("_", "-")
        return normalized.lower()

    def get_streaming_mode_for_model(self, model_name: str) -> str:
        """Return streaming mode ('stream' or 'buffered') for the given model."""
        if not model_name:
            return self.default_streaming_mode

        mode = self.model_streaming_modes.get(model_name.lower())
        if mode:
            return mode

        # Attempt lookup using sanitized key (hyphen replaced with underscore) for safety
        sanitized_key = model_name.lower().replace("-", "_")
        return self.model_streaming_modes.get(sanitized_key, self.default_streaming_mode)
    
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
