variable "region" {
  description = "AWS region to deploy into."
  type        = string
  default     = "eu-west-1"   
}

variable "project" {
  description = "Name prefix applied to every resource so they're easy to find and destroy."
  type        = string
  default     = "payment-auth"
}

variable "cluster_version" {
  description = "Kubernetes version for the EKS control plane."
  type        = string
  default     = "1.30"
}