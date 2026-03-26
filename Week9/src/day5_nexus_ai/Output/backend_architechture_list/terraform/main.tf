provider "aws" {
  region = "us-west-2"
}

resource "aws_dynamodb_table" "tasks" {
  name           = "tasks"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "title"
    type = "S"
  }

  attribute {
    name = "description"
    type = "S"
  }

  attribute {
    name = "due_date"
    type = "S"
  }
}

resource "aws_dynamodb_table" "lists" {
  name           = "lists"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "title"
    type = "S"
  }

  attribute {
    name = "tasks"
    type = "L"
  }
}

resource "aws_api_gateway_rest_api" "todo_list" {
  name        = "TodoListAPI"
  description = "Todo list API"
}

resource "aws_api_gateway_resource" "tasks" {
  rest_api_id = aws_api_gateway_rest_api.todo_list.id
  parent_id   = aws_api_gateway_rest_api.todo_list.root_resource_id
  path_part   = "tasks"
}

resource "aws_api_gateway_method" "get_tasks" {
  rest_api_id = aws_api_gateway_rest_api.todo_list.id
  resource_id = aws_api_gateway_resource.tasks.id
  http_method = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "get_tasks" {
  rest_api_id = aws_api_gateway_rest_api.todo_list.id
  resource_id = aws_api_gateway_resource.tasks.id
  http_method = aws_api_gateway_method.get_tasks.http_method
  integration_http_method = "POST"
  type        = "LAMBDA"
  uri         = "arn:aws:apigateway:us-west-2:lambda:path/2015-03-31/functions/arn:aws:lambda:us-west-2:123456789012:function:get_tasks/invocations"
}

resource "aws_lambda_function" "get_tasks" {
  filename      = "lambda_function_payload.zip"
  function_name = "get_tasks"
  handler       = "index.handler"
  runtime       = "nodejs14.x"
  role          = "arn:aws:iam::123456789012:role/service-role/lambda-execution-role"
}

resource "aws_api_gateway_deployment" "todo_list" {
  depends_on = [aws_api_gateway_integration.get_tasks]
  rest_api_id = aws_api_gateway_rest_api.todo_list.id
  stage_name  = "test"
}