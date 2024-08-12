import os

import boto3


def get_dynamo_client():
    table_name = os.environ.get("TABLE_NAME")

    return boto3.resource("dynamodb").Table(table_name)
