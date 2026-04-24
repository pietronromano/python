#!/usr/bin/env python3
"""
Query all Azure API Management instances across tenant for APIs using sql-data-source resolver policy.
Requires: pip install azure-cli-core azure-mgmt-apimanagement azure-identity
"""

import json
import sys
from typing import List, Dict
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient
from azure.mgmt.resource import SubscriptionClient

def get_all_subscriptions(credential) -> List[str]:
    """Get all subscription IDs in the tenant."""
    subscription_client = SubscriptionClient(credential)
    subscriptions = [sub.subscription_id for sub in subscription_client.subscriptions.list()]
    print(f"Found {len(subscriptions)} subscriptions in tenant")
    return subscriptions

def check_apim_for_sql_policies(subscription_id: str, credential) -> List[Dict]:
    """Check all APIM instances in a subscription for sql-data-source policies."""
    results = []
    
    try:
        client = ApiManagementClient(credential, subscription_id)
        
        # Get all APIM instances in subscription
        apim_instances = list(client.api_management_service.list())
        
        if not apim_instances:
            return results
            
        print(f"\n  Subscription: {subscription_id}")
        print(f"  Found {len(apim_instances)} APIM instance(s)")
        
        for apim in apim_instances:
            apim_name = apim.name
            rg_name = apim.id.split('/')[4]  # Extract resource group from resource ID
            
            print(f"    Checking APIM: {apim_name} in RG: {rg_name}")
            
            try:
                # Get all APIs in this APIM instance
                apis = list(client.api.list_by_service(rg_name, apim_name))
                
                for api in apis:
                    try:
                        # Get API policy
                        policy = client.api_policy.get(
                            rg_name, 
                            apim_name, 
                            api.name
                        )
                        
                        # Check if policy contains sql-data-source
                        policy_content = policy.value if hasattr(policy, 'value') else str(policy)
                        
                        if 'sql-data-source' in policy_content.lower():
                            print(f"      ✓ FOUND: API '{api.display_name}' (ID: {api.name}) uses sql-data-source resolver")
                            
                            results.append({
                                'subscription': subscription_id,
                                'apim': apim_name,
                                'resourceGroup': rg_name,
                                'apiId': api.name,
                                'apiName': api.display_name,
                                'apiPath': api.path
                            })
                    except Exception as e:
                        # API might not have a policy, skip
                        if 'ResourceNotFound' not in str(e):
                            print(f"      Warning: Could not get policy for API {api.name}: {e}")
                        
            except Exception as e:
                print(f"      Error accessing APIM {apim_name}: {e}")
                
    except Exception as e:
        print(f"  Error in subscription {subscription_id}: {e}")
    
    return results

def main():
    """Main execution function."""
    print("=" * 60)
    print("Azure APIM SQL Data Source Policy Scanner")
    print("=" * 60)
    print("\nAuthenticating with Azure...")
    
    try:
        # Use DefaultAzureCredential (works with az login)
        credential = DefaultAzureCredential()
        
        # Get all subscriptions
        print("\nFetching subscriptions...")
        subscription_ids = get_all_subscriptions(credential)
        
        # Scan all subscriptions
        all_results = []
        for sub_id in subscription_ids:
            results = check_apim_for_sql_policies(sub_id, credential)
            all_results.extend(results)
        
        # Save results
        output_file = "apim-sql-resolver-results.json"
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"Scan Complete!")
        print("=" * 60)
        print(f"Total APIs with sql-data-source resolver found: {len(all_results)}")
        print(f"Results saved to: {output_file}")
        
        if all_results:
            print("\nSummary:")
            for result in all_results:
                print(f"  • {result['apim']}/{result['apiName']} (RG: {result['resourceGroup']})")
        
        print("\nFull results:")
        print(json.dumps(all_results, indent=2))
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
