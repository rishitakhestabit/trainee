import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table_name = 'lists'

def create_list(list):
    try:
        table = dynamodb.Table(table_name)
        table.put_item(
            Item={
                'id': list.id,
                'title': list.title,
                'tasks': list.tasks
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])

def get_list(list_id):
    try:
        table = dynamodb.Table(table_name)
        response = table.get_item(Key={'id': list_id})
        return response['Item']
    except ClientError as e:
        print(e.response['Error']['Message'])

def update_list(list_id, list):
    try:
        table = dynamodb.Table(table_name)
        table.update_item(
            Key={'id': list_id},
            UpdateExpression='set title = :title, tasks = :tasks',
            ExpressionAttributeValues={
                ':title': list.title,
                ':tasks': list.tasks
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])

def delete_list(list_id):
    try:
        table = dynamodb.Table(table_name)
        table.delete_item(Key={'id': list_id})
    except ClientError as e:
        print(e.response['Error']['Message'])