#!/bin/bash
# Fix Azure AI Search RBAC permissions

# Load environment variables
source /Users/macbookpro/dev/python/github/python/foundry-mine/.env

# Get the current logged-in user's UPN (User Principal Name)
USER_UPN=$(az ad signed-in-user show --query userPrincipalName -o tsv)
echo "Current user: $USER_UPN"

# Get the Search resource ID
SEARCH_RESOURCE_ID="/subscriptions/$AZURE_SUBSCRIPTION_ID/resourceGroups/$AZURE_RESOURCE_GROUP/providers/Microsoft.Search/searchServices/$AZURE_SEARCH_SERVICE_NAME"
echo "Search Resource ID: $SEARCH_RESOURCE_ID"

# Assign Search Service Contributor role (to create indexes)
echo "Assigning Search Service Contributor role..."
az role assignment create \
    --role "Search Service Contributor" \
    --assignee "$USER_UPN" \
    --scope "$SEARCH_RESOURCE_ID"

# Assign Search Index Data Contributor role (to upload documents)
echo "Assigning Search Index Data Contributor role..."
az role assignment create \
    --role "Search Index Data Contributor" \
    --assignee "$USER_UPN" \
    --scope "$SEARCH_RESOURCE_ID"

# Assign Search Index Data Reader role (to query)
echo "Assigning Search Index Data Reader role..."
az role assignment create \
    --role "Search Index Data Reader" \
    --assignee "$USER_UPN" \
    --scope "$SEARCH_RESOURCE_ID"

echo ""
echo "✅ Role assignments completed!"
echo ""
echo "Verifying role assignments..."
az role assignment list \
    --scope "$SEARCH_RESOURCE_ID" \
    --assignee "$USER_UPN" \
    --output table

echo ""
echo "⚠️  Note: It may take a few minutes for permissions to propagate."
echo "   Try running your script again in 2-3 minutes."
