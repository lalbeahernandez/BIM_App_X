terraform {
  required_version = ">= 1.7.0"
}

# TODO(PROD): choose cloud provider and instantiate organization-approved modules.
# Keep state remote, encrypted and locked. Never store secrets in tfvars committed to Git.
