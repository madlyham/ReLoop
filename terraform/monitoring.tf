resource "aws_cloudwatch_log_group" "api" {
  name              = "/aws/lambda/${var.project_prefix}-api"
  retention_in_days = 7
}

resource "aws_sns_topic" "alerts" {
  name         = "${var.project_prefix}-alerts"
  display_name = "ReLoop Alerts"
  tags         = var.common_tags
}

resource "aws_sns_topic_subscription" "alerts_email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${var.project_prefix}-lambda-errors"
  alarm_description   = "Lambda API errors >= 3 in 5 minutes"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  datapoints_to_alarm = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 3
  treat_missing_data  = "notBreaching"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    FunctionName = aws_lambda_function.api.function_name
  }
}
