
resource "null_resource" "package_lambda" {

  triggers = {
    timestamp = timestamp()
  }

  provisioner "local-exec" {
    command = <<-EOT
     mkdir "./lambda_function_package"
     pip install -r "${path.module}/../../../data/requirements.txt" -t "${path.module}/lambda_function_package"
     cp -r "${path.module}/../../../data/electricity_bidding_data" "${path.module}/lambda_function_package"
     cp -r "${path.module}/lambda_function/lambda_function.py" "${path.module}/lambda_function_package"
     EOT
    interpreter = ["/bin/bash", "-c"]
  }
}

data "archive_file" "lambda_function" {
  depends_on  = [null_resource.package_lambda]
  type = "zip"
  source_dir  = "${path.module}/lambda_function_package/"
  output_path = "${path.module}/extract_semo_lambda_function.zip"
}

resource "aws_s3_object" "lambda_extract_semo" {
  bucket = var.lambda_s3_bucket_info.id
  key    = "extract_semo_lambda_function_${timestamp()}.zip"
  source = data.archive_file.lambda_function.output_path
}

resource "null_resource" "package_lambda_clean" {

  triggers = {
    timestamp = timestamp()
  }

  depends_on  = [aws_s3_object.lambda_extract_semo]
  provisioner "local-exec" {
    command = "rm -rf ${path.module}/lambda_function_package"
    interpreter = ["/bin/bash", "-c"]
  }
}


# LAMBDA
resource "aws_lambda_function" "lambda_function" {
  function_name = "${var.lambda_function_name}-${var.env}"

  s3_bucket = var.lambda_s3_bucket_info.id
  s3_key    = aws_s3_object.lambda_extract_semo.key

  runtime = "python3.11"
  handler = "lambda_function.handler"

  source_code_hash = data.archive_file.lambda_function.output_base64sha256

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
        Resource = var.lambda_s3_bucket_info.arn
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "policy_attachment_s3" {
  role       = aws_iam_role.lambda_exec_and_s3.name
  policy_arn = aws_iam_policy.policy_s3.arn
}


