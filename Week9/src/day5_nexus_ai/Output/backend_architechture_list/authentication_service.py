import boto3
from botocore.exceptions import ClientError

cognito_idp = boto3.client('cognito-idp')

def authenticate_user(username, password):
    try:
        response = cognito_idp.admin_initiate_auth(
            UserPoolId='your-user-pool-id',
            ClientId='your-client-id',
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        return response['AuthenticationResult']['IdToken']
    except ClientError as e:
        print(e.response['Error']['Message'])

def authenticate_user_from_token(token):
    try:
        response = cognito_idp.get_user(
            AccessToken=token
        )
        return response['UserAttributes']
    except ClientError as e:
        print(e.response['Error']['Message'])