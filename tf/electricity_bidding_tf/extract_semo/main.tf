
data "archive_file" "lambda_process_request" {
  type = "zip"
  source_dir  = "${path.module}/lambda_function/"
  output_path = "${path.module}/lambda_function.zip"
}

resource "aws_s3_object" "lambda_extract_semo" {
  bucket = var.lambda_s3_bucket_id
  key    = "lambda_function.zip"
  source = data.archive_file.lambda_process_request.output_path
  etag = filemd5(data.archive_file.lambda_process_request.output_path)
}

# LAMBDA
resource "aws_lambda_function" "lambda_function" {
  function_name = "${var.lambda_function_name}_${var.env}"

  s3_bucket = aws_s3_bucket.lambda_bucket.id
  s3_key    = aws_s3_object.lambda_extract_semo.key

  runtime = "python3.11"
  handler = "lambda_function.extract_semo.py"

  source_code_hash = data.archive_file.lambda_process_request.output_base64sha256

  # Amazon Resource Number...uniquely identifies AWS resources.
  role = aws_iam_role.lambda_exec_and_dynamo.arn

  environment {
    variables = {
      ENV = var.env
    }
  }
}

resource "aws_cloudwatch_log_group" "melostats_process_request" {
  name = "/aws/lambda/${aws_lambda_function.process_request.function_name}"
  retention_in_days = 30
}

resource "aws_iam_role" "lambda_exec_and_dynamo" {
  name = "serverless_lambda"

  # I think this says that only lamda can use the role.
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      # This says that only lambda service can assume this role
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      }
    ]
  })
}

# Attach basic execution policy
resource "aws_iam_role_policy_attachment" "lambda_exec_policy_attachment" {
  role       = aws_iam_role.lambda_exec_and_dynamo.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Attach Dynamo execution
resource "aws_iam_policy" "policy_dynamo_add" {
  name        = "policy_dynamo_add"
  description = "Add metrics to Dynamo"

  policy = jsonencode({
    Version = "2012-10-17"
    # I wonder is it better to have a single policy with dynamo and lambda execute.
    Statement = [
      {
        Action = [
          "dynamodb:BatchWriteItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem"
        ]
        Effect   = "Allow"
        Resource = aws_dynamodb_table.melostats_db.arn
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_dynamo_policy_attachment" {
  role       = aws_iam_role.lambda_exec_and_dynamo.name
  policy_arn = aws_iam_policy.policy_dynamo_add.arn
}
