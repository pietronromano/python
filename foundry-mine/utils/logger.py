# utils/logger.py

from enum import Enum
import logging
import logging.config
import yaml
import traceback

"""

Utility class for logging messages with different levels (info, warning, error) and optional timestamps.
NOTE: Python Docs are not very clear about logging, in particual how to load configuration from a YAML file

Twelve-Factor App Principles for Logging:
- A twelve-factor app never concerns itself with routing or storage of its output stream. 
- It should not attempt to write to or manage logfiles. Instead, each running process writes its event stream, unbuffered, to stdout. 
- During local development, the developer will view this stream in the foreground of their terminal to observe the app’s behavior.
 
Levels are used to categorize logs by severity
- DEBUG: 🐛 Detailed diagnostic information.
- INFO: ℹ️✅ Confirmation that things are working as expected.
- WARNING: ⚠️ Indication that something unexpected happened (default level).
- ERROR: ❌ A more serious problem; the software couldn't perform a function.
- CRITICAL: 💀 A serious error; the program itself may be unable to continue



# References:
 - The Twelve-Factor App, X1. Logs: https://12factor.net/logs
 - Python Docs:
    - Logging HOWTO: https://docs.python.org/3/howto/logging.html
    - Logging Cookbook: https://docs.python.org/3/howto/logging-cookbook.html
    - Logging Configuration API: https://docs.python.org/3/library/logging.config.html#logging-config-api
    - traceback: https://docs.python.org/3/library/traceback.html
 - Packt: Modern Python Cookbook: 13.6 Using logging for control and audit output

"""

# Simple enum to avoid having client code directly reference logging module constants
class UtilsLogLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

# Utility class for logging messages with different levels
class UtilsLogger:
    def __init__(self, name: str = __name__, logger_config_path: str = 'config/logger.yml'):
        try:    
            # NOTE: Python Docs are not very clear about logging, in particular how to load configuration from a YAML file
            # Load and parse the YAML configuration file
            with open(logger_config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Configure logging using the parsed dictionary
            logging.config.dictConfig(config)
            
            # Create logger
            self.logger = logging.getLogger(name)
        except Exception as e:
            print(f"\n❌ Error initializing logger: {e}")
            self.logger = None
    #end of function: __init__  


    def manual_init_example(self, name: str = __name__, level: UtilsLogLevel = UtilsLogLevel.INFO):
        """Example of how to manually initialize a logger without using the __init__ method."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level.value)
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def log(self, message: str, level: UtilsLogLevel = UtilsLogLevel.INFO, exc: Exception = None):
        """Log a message with the specified level."""
        if self.logger is None:
            print(f"❌ Logger not initialized. Message: {message}")
            return
        
        # Remove line breaks from message to ensure each log entry is a single line (best practice for log parsing)
        message = message.replace('\n', ' ').replace('\r', '')

        match level:
            case UtilsLogLevel.DEBUG:
                self.logger.debug(f"🐛 {message}")
            case UtilsLogLevel.INFO:
                self.logger.info(f"✅ {message}")
            case UtilsLogLevel.WARNING:
                self.logger.warning(f"⚠️ {message}")
            case UtilsLogLevel.ERROR:
                self.logger.error(f"❌ {message}")
            case UtilsLogLevel.CRITICAL:
                self.logger.critical(f"💀 {message}")
            case _:
                self.logger.info(f"ℹ️ {message} (Default to INFO if level is unrecognized)")  # Default to INFO if level is unrecognized
    
        if exc is not None:
            exc_message = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            self.logger.error(f"Exception details: {exc_message}")

    #end of function

    def debug(self, message: str):
        """Log a debug message."""
        self.log(message, UtilsLogLevel.DEBUG)
    def info(self, message: str):
        """Log an info message."""
        self.log(message, UtilsLogLevel.INFO)
    def warning(self, message: str):
        """Log a warning message."""
        self.log(message, UtilsLogLevel.WARNING)

    def error(self, message: str, exc: Exception = None):
        """Log an error message."""
        self.log(message, UtilsLogLevel.ERROR, exc=exc)
    def critical(self, message: str, exc: Exception = None):
        """Log a critical message."""
        self.log(message, UtilsLogLevel.CRITICAL, exc=exc)

    