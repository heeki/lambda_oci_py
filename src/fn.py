import base64
import boto3
import json
import os
from lib.customer import Customer


# helper functions
def build_response(code, body):
    # headers for cors
    headers = {
        "Access-Control-Allow-Origin": "amazonaws.com",
        "Access-Control-Allow-Credentials": True
    }

    # lambda proxy integration
    response = {
        'isBase64Encoded': False,
        'statusCode': code,
        'headers': headers,
        'body': body
    }

    return response


# function: lambda invoker handler
def handler(event, context):
    print(json.dumps(event))
    method = event["requestContext"]["http"]["method"] 

    if method == "GET":
        response = customer.get_all()
        status = response["HTTPStatusCode"]
        output = build_response(status, json.dumps(response["ResponseBody"]))
    
    elif method == "POST":
        # TODO: need to implement request body validation
        if "body" in event:
            body = json.loads(base64.b64decode(event["body"]))
            customer.set_given_name(body["given_name"])
            customer.set_family_name(body["family_name"])
            customer.set_birthdate(body["birthdate"])
            customer.set_email(body["email"])
            customer.set_phone_number(body["phone_number"])
            customer.set_phone_number_verified(body["phone_number_verified"])
            response = customer.create()
            print(response)
        else:
            response = {
                "HTTPStatusCode": 500,
                "ResponseBody": {
                    "ErrorMessage": "Request body is missing",
                    "ErrorType": "InputError"
                }
            }
        status = response["HTTPStatusCode"]
        payload = str(customer) if status == 200 else json.dumps(response["ResponseBody"])
        output = build_response(status, payload)

    print(output)
    return output


# initialization, mapping
ddb = boto3.client("dynamodb")
table = os.environ["TABLE"]
customer = Customer(ddb, table)