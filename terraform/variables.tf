variable "aws_region" {
  description = "Primary AWS region for ReLoop regional services"
  type        = string
  default     = "ap-southeast-1"
}

variable "project_prefix" {
  description = "Resource name prefix (e.g., reloop2)"
  type        = string
  default     = "reloop2"
}

variable "bucket_suffix" {
  description = "Short unique suffix appended to globally unique S3 bucket names and default Cognito domain"
  type        = string
}

variable "cognito_domain_prefix" {
  description = "Optional custom Cognito domain prefix; defaults to <project_prefix>-auth-<bucket_suffix>"
  type        = string
  default     = ""
}

variable "cognito_deletion_protection" {
  description = "Cognito User Pool deletion protection (ACTIVE or INACTIVE; set INACTIVE before terraform destroy)"
  type        = string
  default     = "ACTIVE"
}

variable "alert_email" {
  description = "Admin email subscribed to SNS CloudWatch alarm notifications"
  type        = string
  sensitive   = true
}

variable "origin_verify_secret" {
  description = "64-hex shared secret sent by CloudFront in x-origin-verify header to Lambda"
  type        = string
  sensitive   = true
}

variable "ai_model_id" {
  description = "Amazon Bedrock cross-region inference profile ID for device photo analysis"
  type        = string
  default     = "global.moonshotai.kimi-k3"
}

variable "api_zip_path" {
  description = "Path to built backend API Lambda zip package"
  type        = string
  default     = "../zips/reloop2-api.zip"
}

variable "post_confirmation_zip_path" {
  description = "Path to Cognito Post-Confirmation Lambda zip package"
  type        = string
  default     = "../zips/reloop2-post-confirmation.zip"
}

variable "role_permissions_boundary_name" {
  description = "Optional IAM managed policy name used as permissions boundary for Lambda roles (leave empty on personal accounts)"
  type        = string
  default     = ""
}

variable "cloudfront_cors_origins" {
  description = "Optional extra CloudFront HTTPS origins added to API Gateway CORS (pass after first apply to avoid a Terraform dependency cycle)"
  type        = list(string)
  default     = []
}

variable "web_origin_id" {
  description = "CloudFront origin ID for the private S3 website bucket"
  type        = string
  default     = "s3-web"
}

variable "common_tags" {
  description = "Standard tags applied to workshop resources"
  type        = map(string)
  default = {
    Project = "reloop2"
    Purpose = "workshop"
  }
}
