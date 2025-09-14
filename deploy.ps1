$PROJECT_PATH = "C:\Users\javier\Documents\20252_code\s202514-proyecto-grupo19"

echo "Deploying EKS Cluster..."
echo "Planning Terraform configuration..."
terraform -chdir="$PROJECT_PATH/terraform/stacks/eks" plan -var-file="$PROJECT_PATH/terraform/environments/deployment/eks/terraform.tfvars" -out=".tfplan"
echo "Applying Terraform configuration..."
terraform -chdir="$PROJECT_PATH/terraform/stacks/eks" apply ".tfplan"
