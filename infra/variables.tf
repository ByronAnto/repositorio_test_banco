# Variables definition file for Terraform configuration

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "production"
}

variable "tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "Banking-DevOps"
    ManagedBy   = "Terraform"
    Team        = "DevOps"
  }
}
