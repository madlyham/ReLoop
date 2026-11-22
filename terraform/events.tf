resource "aws_cloudwatch_event_rule" "sweep" {
  name                = "${var.project_prefix}-sweep"
  description         = "ReLoop: expire open listings every 15 minutes"
  schedule_expression = "rate(15 minutes)"
  state               = "ENABLED"
}

resource "aws_cloudwatch_event_target" "sweep_lambda" {
  rule      = aws_cloudwatch_event_rule.sweep.name
  target_id = "ReLoopSweepLambda"
  arn       = aws_lambda_function.api.arn
}

resource "aws_lambda_permission" "eventbridge_sweep" {
  statement_id  = "AllowEventBridgeSweep"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.sweep.arn
}
