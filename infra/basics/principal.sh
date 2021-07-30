spName=lis-project-acr

# Create a service principal and get password
spPassword=$(az ad sp create-for-rbac --name $spName --query password --output tsv)
# Get service principal application id
spAppId=$(az ad sp list --display-name $spName --query [].appId --output tsv)
# Get service principal object id
spObjectId=$(az ad sp list --display-name $spName --query [].objectId --output tsv)

echo "name: $spName"
echo "appId: $spAppId"
echo "objectId: $spObjectId"
echo "password: $spPassword"
