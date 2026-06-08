output "cluster_name" {
  description = "EKS cluster name."
  value       = module.eks.cluster_name
}

output "ecr_url" {
  description = "Repository URL to tag and push the image to."
  value       = aws_ecr_repository.app.repository_url
}

output "configure_kubectl" {
  description = "Run this to set up kubectl access."
  value       = "aws eks update-kubeconfig --region ${var.region} --name ${module.eks.cluster_name}"
}