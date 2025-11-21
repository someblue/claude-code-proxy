#!/usr/bin/env python3
"""
Test script for multi-API-key functionality
"""

import os
import sys
import tempfile
from unittest.mock import patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_multi_key_config():
    """Test the multi-key configuration loading"""
    
    # Set up test environment variables
    test_env = {
        'OPENAI_API_KEY': 'test-openai-key',
        'BIG_MODEL': 'gpt-4o',
        'MIDDLE_MODEL': 'gpt-4o',
        'SMALL_MODEL': 'gpt-4o-mini',
        
        # Multi-key mappings
        'API_KEY_MODEL_MAPPING_PREMIUM_API_KEY': 'premium-user-key',
        'API_KEY_MODEL_MAPPING_PREMIUM_BIG': 'gpt-4o',
        'API_KEY_MODEL_MAPPING_PREMIUM_MIDDLE': 'gpt-4o',
        'API_KEY_MODEL_MAPPING_PREMIUM_SMALL': 'gpt-4o-mini',
        'API_KEY_MODEL_MAPPING_PREMIUM_IGNORE_TEMPERATURE': 'false',
        
        'API_KEY_MODEL_MAPPING_BASIC_API_KEY': 'basic-user-key',
        'API_KEY_MODEL_MAPPING_BASIC_BIG': 'gpt-3.5-turbo',
        'API_KEY_MODEL_MAPPING_BASIC_MIDDLE': 'gpt-3.5-turbo',
        'API_KEY_MODEL_MAPPING_BASIC_SMALL': 'gpt-3.5-turbo',
        'API_KEY_MODEL_MAPPING_BASIC_IGNORE_TEMPERATURE': 'true',
    }
    
    with patch.dict(os.environ, test_env, clear=True):
        from src.core.config import Config
        from src.core.model_manager import ModelManager
        from src.core.context import set_current_api_key
        
        # Test config loading
        config = Config()
        
        print("✓ Config loaded successfully")
        print(f"  Default models: BIG={config.big_model}, MIDDLE={config.middle_model}, SMALL={config.small_model}")
        print(f"  API key mappings: {len(config.api_key_model_mapping)} keys configured")
        
        # Test API key validation
        assert config.validate_client_api_key('premium-user-key') == True
        assert config.validate_client_api_key('basic-user-key') == True
        assert config.validate_client_api_key('unknown-key') == False
        print("✓ API key validation works correctly")
        
        # Test model selection for different API keys
        model_manager = ModelManager(config)
        
        # Test premium user
        set_current_api_key('premium-user-key')
        assert model_manager.map_claude_model_to_openai('claude-3-5-sonnet-20241022') == 'gpt-4o'
        assert model_manager.map_claude_model_to_openai('claude-3-haiku-20240307') == 'gpt-4o-mini'
        print("✓ Premium user model mapping works correctly")
        
        # Test basic user
        set_current_api_key('basic-user-key')
        assert model_manager.map_claude_model_to_openai('claude-3-5-sonnet-20241022') == 'gpt-3.5-turbo'
        assert model_manager.map_claude_model_to_openai('claude-3-haiku-20240307') == 'gpt-3.5-turbo'
        print("✓ Basic user model mapping works correctly")
        
        # Test unknown API key (should use defaults)
        set_current_api_key('unknown-key')
        assert model_manager.map_claude_model_to_openai('claude-3-5-sonnet-20241022') == 'gpt-4o'
        assert model_manager.map_claude_model_to_openai('claude-3-haiku-20240307') == 'gpt-4o-mini'
        print("✓ Fallback to default models works correctly")
        
        # Test backwards compatibility (no API key set)
        set_current_api_key(None)
        assert model_manager.map_claude_model_to_openai('claude-3-5-sonnet-20241022') == 'gpt-4o'
        assert model_manager.map_claude_model_to_openai('claude-3-haiku-20240307') == 'gpt-4o-mini'
        print("✓ Backwards compatibility works correctly")
        
        # Test ignore temperature settings
        set_current_api_key('premium-user-key')
        premium_config = config.get_models_for_api_key('premium-user-key')
        assert premium_config['ignore_temperature'] == False
        print("✓ Premium user temperature settings correct")
        
        set_current_api_key('basic-user-key')
        basic_config = config.get_models_for_api_key('basic-user-key')
        assert basic_config['ignore_temperature'] == True
        print("✓ Basic user temperature settings correct")

def test_legacy_single_key():
    """Test that the system still works with legacy single-key configuration"""
    
    test_env = {
        'OPENAI_API_KEY': 'test-openai-key',
        'ANTHROPIC_API_KEY': 'single-legacy-key',
        'BIG_MODEL': 'gpt-4o',
        'MIDDLE_MODEL': 'gpt-4o',
        'SMALL_MODEL': 'gpt-4o-mini',
    }
    
    with patch.dict(os.environ, test_env, clear=True):
        from src.core.config import Config
        from src.core.model_manager import ModelManager
        
        config = Config()
        
        # Test legacy API key validation
        assert config.validate_client_api_key('single-legacy-key') == True
        assert config.validate_client_api_key('wrong-key') == False
        print("✓ Legacy single-key validation works correctly")
        
        # Test model selection (should use defaults)
        model_manager = ModelManager(config)
        assert model_manager.map_claude_model_to_openai('claude-3-5-sonnet-20241022') == 'gpt-4o'
        assert model_manager.map_claude_model_to_openai('claude-3-haiku-20240307') == 'gpt-4o-mini'
        print("✓ Legacy model mapping works correctly")

if __name__ == '__main__':
    print("Testing multi-API-key functionality...")
    print()
    
    try:
        test_multi_key_config()
        print()
        test_legacy_single_key()
        print()
        print("🎉 All tests passed! The multi-API-key functionality is working correctly.")
        print()
        print("Usage example:")
        print("1. Configure multiple API keys in .env using the format shown in .env.multi-key.example")
        print("2. Different clients can use different API keys to get different model tiers")
        print("3. Existing single-key configurations continue to work without changes")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)