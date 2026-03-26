import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table_name = 'tasks'

def create_task(task):
    try:
        table = dynamodb.Table(table_name)
        table.put_item(
            Item={
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'due_date': task.due_date
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])

def get_task(task_id):
    try:
        table = dynamodb.Table(table_name)
        response = table.get_item(Key={'id': task_id})
        return response['Item']
    except ClientError as e:
        print(e.response['Error']['Message'])

def update_task(task_id, task):
    try:
        table = dynamodb.Table(table_name)
        table.update_item(
            Key={'id': task_id},
            UpdateExpression='set title = :title, description = :description, due_date = :due_date',
            ExpressionAttributeValues={
                ':title': task.title,
                ':description': task.description,
                ':due_date': task.due_date
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])

def delete_task(task_id):
    try:
        table = dynamodb.Table(table_name)
        table.delete_item(Key={'id': task_id})
    except ClientError as e:
        print(e.response['Error']['Message'])