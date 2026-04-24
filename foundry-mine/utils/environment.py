# utils/env_vars.py

import sys

from dotenv import load_dotenv
import os
import importlib

"""
Utility class for loading and managing environment variables from a .env file. 

Pre-requisites: 
    - python-dotenv==1.0.0  

References:
    - Udemy: https://www.udemy.com/course/microsoft-foundry/learn/lecture/54848481#overview
    - python-dotenv documentation: https://pypi.org/project/python-dotenv/
    - Best practices for managing environment variables in Python: https://12factor.net/config
"""

class UtilsEnvironment:
    @staticmethod
    def load_env_vars(env_file_path: str = "config/.env") -> bool:
        """
        Load environment variables from the specified .env file and store them in a dictionary.
        
        Args:
            env_file_path: The path to the .env file (default is "config/.env": config folder in the root of the project)

        Returns:
            True if loading was successful, False otherwise
        """
        print("=" * 60)
        print("Loading Environment Variables")
        print("=" * 60)
    
        # Read .env file and extract all keys automatically
        env_settings = {}
        env_keys = []
        try:
            with open(env_file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        # Extract key from KEY=VALUE format
                        if '=' in line:
                            key = line.split('=', 1)[0].strip()
                            env_keys.append(key)
        except FileNotFoundError:
            print(f"❌ .env file not found at {env_file_path}")
            return None
        
        # Load the .env file — this must run before we read any values
        # override=False ensures that existing environment variables (e.g. set in Azure) are not overwritten by .env file values
        load_dotenv(env_file_path, override=False)  
        
        # Read each setting from the environment and store in dictionary
        for key in env_keys:
            env_settings[key] = os.getenv(key)
            # Check for value, print result
            if env_settings[key]:
                print(f"✅ {key}: {env_settings[key]}")
            else:
                print(f"❌ {key} not set")
                return None
        return env_settings
    # end of function

    @staticmethod
    def check_required_packages(requirements_path: str = "config/requirements.txt") -> bool:
        """Check required packages"""
        print("Checking Required Packages")

        # Read required packages from requirements.txt
        required_packages = [] 
        try:
            with open(requirements_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        # Extract package name (before == or >=, etc.)
                        package = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                        
                        # Convert pip package names to Python import names
                        # pip uses hyphens, Python imports use dots or different names
                        if package == 'python-dotenv':
                            package = 'dotenv'
                        elif package.startswith('azure-'):
                        # Azure packages: azure-ai-projects -> azure.ai.projects
                            package = package.replace('-', '.')
                        # Special case for pyyaml which is imported as yaml
                        elif package == 'pyyaml':
                            package = 'yaml'  # pyyaml is imported as yaml

                        required_packages.append(package)
        except FileNotFoundError:
            print(f"❌ requirements.txt not found at {requirements_path}")
            return False
        
        # Check each package
        for package in required_packages:
            try:
                module = importlib.import_module(package)
                
                # Try to get version if available
                version = getattr(module, '__version__', None)
                if version:
                    print(f"✅ {package} {version}")
                else:
                    print(f"✅ {package} installed")
            except ImportError:
                print(f"❌ {package} not installed")
                return False
        return True
    # end of function

    @staticmethod
    def check_python_version(desired_major: int = 3, desired_minor: int = 12) -> tuple[int, int]:
        """Check Python version
        
        Args:
            desired_major: The major version number to check for (default is 3)
            desired_minor: The minor version number to check for (default is 12)
        
        Returns:
            True if the Python version matches the desired version, False otherwise

        """
        print("Checking Python Version")
        
        # Store version and path
        python_version = sys.version_info[:2]     
        print(f"Python: {sys.version}")
        print(f"Path:   {sys.executable}")

        major, minor = python_version
        print(f"Python Version dectected: {major}.{minor}")
        if minor == desired_minor and major == desired_major:
            return True
        else:
            print(f"⚠️  Python {major}.{minor} detected — {desired_major}.{desired_minor} is recommended ({desired_major}.{desired_minor+2}+ has compatibility issues)")

    # end of function
  