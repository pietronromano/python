import pytest
from foundry.setup import FoundrySetup

# Shared fixture for all tests
# This fixture initializes the Foundry environment and clients before running tests
@pytest.fixture
def test_setup():
    setup = FoundrySetup()

    # Step 1: Load environment variables (before checking for required packages, as some package checks may depend on env vars)
    assert setup.load_environment_config(), "load_environment_config failed"

    # Step 2: Check Python version
    assert setup.check_python_version(3,12), "Python version should be 3.12"

   # Step 3: Check required packages
    assert setup.check_required_packages(), "check_required_packages failed"

    # Step 4: Login to Azure using DefaultAzureCredential (NOTE: also creates  mgmt_client and project_client)
    assert setup.login_azure_clients(), "login_azure_clients failed"
    
    # Step 5: Check Azure CLI login (OPTIONAL - can be used for manual verification or if you have scripts that rely on Azure CLI authentication)
    # assert setup.check_azure_cli_login(), "check_azure_cli_login failed"
    
    # Return the setup instance for potential use
    return setup
