
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

  s3_bucket = var.lambda_s3_bucket.id
  s3_key    = aws_s3_object.lambda_extract_semo.key

  runtime = "python3.11"
  handler = "lambda_function.extract_semo.py"

  source_code_hash = data.archive_file.lambda_process_request.output_base64sha256

  # Amazon Resource Number...uniquely identifies AWS resources.
  role = aws_iam_role.lambda_exec_and_s3.arn

  environment {
    variables = {
      ENV = var.env
    }
  }
}

resource "aws_cloudwatch_log_group" "lambda_function" {
  name = "/aws/lambda/${aws_lambda_function.lambda_function.function_name}"
  retention_in_days = 30
}

resource "aws_iam_role" "lambda_exec_and_s3" {
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
resource "aws_iam_role_policy_attachment" "policy_attachment_lambda_exec" {
  role       = aws_iam_role.lambda_exec_and_s3.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Attach S3 permissions
resource "aws_iam_policy" "policy_s3" {
  name        = "policy_s3"
  description = "Read and write from S3"

  policy = jsonencode({
    Version = "2012-10-17"
    # I wonder is it better to have a single policy with dynamo and lambda execute.
    Statement = [
      {
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject"
        ]
        Effect   = "Allow"
        Resource = var.lambda_s3_bucket.arn
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "policy_attachment_s3" {
  role       = aws_iam_role.policy_s3.name
  policy_arn = aws_iam_policy.policy_s3.arn
}
