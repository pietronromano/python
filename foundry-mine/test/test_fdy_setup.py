import traceback

import pytest
from foundry.setup import FoundrySetup

# test_setup fixture is in conftest.py and available to all test files

# Run all EXCEPT slow tests: pytest -m "not slow" (see pytest.ini for marker definition)
@pytest.mark.slow
def test_model_deployments(test_setup):   
        setup: FoundrySetup = test_setup
        # List available models for deployment (optional - uncomment if needed)
        models:list = setup.get_available_models()
        assert models is not None and len(models) > 0, "No available models found"

        # List existing deployments
        deployment_list = setup.get_existing_deployments()

        # Check if a specific deployment already exists
        model_name = "gpt-4.1"  # [We use the same as the model itself for the name we want to use for our deployment]
        deployment_exists = setup.check_deployment_exists(model_name)

        # Step 10: Deploy the model if the deployment doesn't already exist
        if not deployment_exists:
            # Verify the model exists in the catalog and get its SKU info
            model_details = setup.get_model_details(model_name)
            
            if model_details["found"]:
                print(f"\n✅ The model '{model_name}' version '{model_details['version']}' is available in the catalog.")
                # Deploy the model
                setup.deploy_model(model_details["name"])
            else:
                print(f"\n⚠️ The model '{model_name}' is NOT available in the catalog.")
                print(f"   Check the available models list above and update the model name if needed.")
        else:
            print(f"\n✅ Deployment '{model_name}' already exists. Skipping deployment step.")


        # Step 11: Test Deployment by creating a response from the deployed model
        instructions_text="You are a friendly and knowledgeable assistant who gives clear, concise answers."
        input_text="What are three practical uses of AI in everyday life?"
        ai_response = setup.prompt_for_response (model_name, instructions_text, input_text)
        print(f"✅ {ai_response.output_text}")
#end of function
