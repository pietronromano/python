
from typing import Annotated
from fastapi import Depends


from foundry.setup import FoundrySetup


# DEBUGGING NOTES: Auto-reload resets everything: When running with uvicorn --reload, 
# any file change restarts the server and resets _foundry_setup_instance = None

# Singleton instance - initialized once and reused
_foundry_setup_instance = None
def get_foundry_setup() -> FoundrySetup:
    """
    Dependency function that returns a singleton FoundrySetup instance.
    Initializes once on first call, then reuses the same instance.
    """
    global _foundry_setup_instance
    if _foundry_setup_instance is None:
        _foundry_setup_instance = FoundrySetup()
        _foundry_setup_instance.load_environment_config()
        _foundry_setup_instance.login_azure_clients()
    return _foundry_setup_instance

# Type alias for the FoundrySetup dependency to reduce repetition in routers
FoundrySetupDependency = Annotated[FoundrySetup, Depends(get_foundry_setup)]






   