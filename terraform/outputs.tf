output "cloudfront_url" {
  value = "https://${aws_cloudfront_distribution.web.domain_name}"
}

output "cloudfront_distribution_id" {
  value = aws_cloudfront_distribution.web.id
}

output "api_endpoint" {
  value = aws_apigatewayv2_api.http.api_endpoint
}

output "cognito_user_pool_id" {
  value = aws_cognito_user_pool.main.id
}

output "cognito_client_id" {
  value = aws_cognito_user_pool_client.web.id
}

output "cognito_domain" {
  value = "https://${aws_cognito_user_pool_domain.auth.domain}.auth.${data.aws_region.current.region}.amazoncognito.com"
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.core.name
}

output "images_bucket_name" {
  value = aws_s3_bucket.images.bucket
}

output "web_bucket_name" {
  value = aws_s3_bucket.web.bucket
}

output "guardrail_id" {
  value = aws_bedrock_guardrail.main.guardrail_id
}

output "sns_topic_arn" {
  value = aws_sns_topic.alerts.arn
}
