import os
import boto3
import datetime

dynamodb = boto3.client('dynamodb')
TABLE_NAME = os.environ['TABLE_NAME']

def lambda_handler(event, context):
    # Ensure this is a PostConfirmation event
    if event.get('triggerSource') != 'PostConfirmation_ConfirmSignUp':
        return event

    user_attributes = event['request']['userAttributes']
    user_id = user_attributes['sub']
    email = user_attributes.get('email', '')
    name = user_attributes.get('name', 'Unknown')
    
    # Spec 4.1: New accounts default to Owner role
    role = 'Owner'
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')

    try:
        dynamodb.put_item(
            TableName=TABLE_NAME,
            Item={
                'PK': {'S': f"USER#{user_id}"},
                'SK': {'S': "PROFILE"},
                'GSI1PK': {'S': f"ROLE#{role}"},
                'GSI1SK': {'S': f"USER#{user_id}"},
                'email': {'S': email},
                'fullName': {'S': name},
                'role': {'S': role},
                'status': {'S': 'ACTIVE'},
                'createdAt': {'S': timestamp}
            },
            # Prevent overwriting an existing user if the trigger fires twice
            ConditionExpression='attribute_not_exists(PK)' 
        )
    except Exception as e:
        print(f"Failed to write user to DynamoDB: {str(e)}")
        # Do not raise the exception; returning the event lets Cognito finish the login
        
    # Cognito triggers MUST return the original event object
    return event