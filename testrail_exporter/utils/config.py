import json
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    """Class for managing application configuration."""
    
    def __init__(self, config_file=None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file (str, optional): Path to config file. If None, uses default path.
        """
        self.home_dir = str(Path.home())
        self.app_dir = os.path.join(self.home_dir, '.testrail_exporter')
        
        # Create app directory if it doesn't exist
        if not os.path.exists(self.app_dir):
            os.makedirs(self.app_dir)
            
        # Set config file path
        if config_file:
            self.config_file = config_file
        else:
            self.config_file = os.path.join(self.app_dir, 'config.json')
            
        # Load or create default config
        self.config = self._load_config()
        
    def _load_config(self):
        """
        Load configuration from file or create default.
        
        Returns:
            dict: Configuration dictionary
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    
                    # Validate config structure
                    if not isinstance(config, dict) or not all(k in config for k in ['testrail', 'export', 'ui']):
                        logger.warning(f"Invalid config format in {self.config_file}. Creating default config.")
                        return self._create_default_config()
                    return config
            else:
                logger.info(f"Config file not found at {self.config_file}. Creating default config.")
                return self._create_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing config file: {str(e)}")
            return self._create_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            return self._create_default_config()
    
    def _create_default_config(self):
        """
        Create default configuration.
        
        Returns:
            dict: Default configuration
        """
        default_config = {
            'testrail': {
                'url': 'https://testrail.testeng.mlbinfra.net',
                'username': '',
                'api_key': ''
            },
            'export': {
                'directory': os.path.join(self.home_dir, 'Documents')
            },
            'ui': {
                'window_width': 1000,
                'window_height': 700,
                'last_project': None
            }
        }
        
        # Save default config to file
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config=None):
        """
        Save configuration to file.
        
        Args:
            config (dict, optional): Configuration to save. If None, uses self.config.
        """
        if config:
            self.config = config
            
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Config saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving config: {str(e)}")
    
    def get_setting(self, section, key, default=None):
        """
        Get a setting from the configuration.
        
        Args:
            section (str): Configuration section
            key (str): Setting key
            default: Default value if setting doesn't exist
            
        Returns:
            Setting value or default
        """
        try:
            return self.config.get(section, {}).get(key, default)
        except Exception:
            return default
    
    def set_setting(self, section, key, value):
        """
        Set a setting in the configuration.
        
        Args:
            section (str): Configuration section
            key (str): Setting key
            value: Setting value
        """
        if section not in self.config:
            self.config[section] = {}
            
        self.config[section][key] = value
        self.save_config()