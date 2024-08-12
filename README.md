# README for Simple Todo Project

## Overview

This project uses AWS CDK to deploy a simple Todo application with a FastAPI CRUD backend hosted on AWS Lambda and a DynamoDB table for data storage.

## Prerequisites

- **AWS Account**: You need an AWS account to deploy this project.
- **AWS CDK**: Make sure you have AWS CDK installed on your machine.
- **Docker**: Docker is required for building the Lambda function image.

## Project Structure

The project consists of the following components:

1. **DynamoDB Table**: Stores todo tasks with a primary key `task_id` and a global secondary index on `user_id`.
2. **AWS Lambda Function**: Hosts the FastAPI CRUD backend.
3. **API Gateway**: Provides a URL for invoking the Lambda function.

## Deployment Steps

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Deploy the Stack**:
   ```bash
   cdk deploy
   ```

3. **Verify Deployment**:
   - Check the CloudFormation console for the deployed stack.
   - Verify that the DynamoDB table and Lambda function are created.

## Usage

1. **Get API URL**:
   - After deployment, the API URL will be output in the CloudFormation console.
   - Use this URL to interact with your FastAPI CRUD backend.

2. **CRUD Operations**:
   - **Create Todo**: `POST /todos`
     ```json
     {
       "content": "Buy milk",
       "user_id": "user123"
     }
     ```
   - **Get All Todos**: `GET /all-todos/{user_id}`
     ```bash
     curl -X GET 'https://your-api-url.com/all-todos/user123'
     ```
   - **Update Todo**: `PUT /todos/{task_id}`
     ```json
     {
       "content": "Buy milk and eggs",
       "user_id": "user123"
     }
     ```
   - **Delete Todo**: `DELETE /todos/{task_id}`

## Code Explanation

### DynamoDB Table

```python
const table = new ddb.Table(this, "Tasks", {
    partitionKey: {name: "task_id", type: ddb.AttributeType.STRING},
    billingMode: ddb.BillingMode.PAY_PER_REQUEST,
    timeToLiveAttribute: "ttl", /* just for testing */
});
```

### Global Secondary Index

```python
table.addGlobalSecondaryIndex({
    indexName: "user-index",
    partitionKey: {name: "user_id", type: ddb.AttributeType.STRING},
    sortKey: {name: "created_time", type: ddb.AttributeType.NUMBER},
});
```

### Lambda Function

```python
const api = new lambda.DockerImageFunction(this, 'API', {
    code: lambda.DockerImageCode.fromImageAsset("../todo-api"),
    memorySize: 1024,
    timeout: cdk.Duration.seconds(10),
    environment: {
        TABLE_NAME: table.tableName,
    },
});
```

### API Gateway

```python
const functionUrl = api.addFunctionUrl({
    authType: lambda.FunctionUrlAuthType.NONE,
    cors: {
        allowedOrigins: ["*"],
        allowedMethods: [lambda.HttpMethod.ALL],
        allowedHeaders: ["*"],
    },
});
```

### Permissions

```python
table.grantReadWriteData(api);
```

## Conclusion

This project demonstrates how to deploy a simple Todo application using AWS CDK, FastAPI, and DynamoDB. The FastAPI CRUD backend is hosted on AWS Lambda, and the API Gateway provides a URL for invoking the Lambda function.