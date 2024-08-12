import time
import uuid

from fastapi import FastAPI, Depends, status, HTTPException
from mangum import Mangum
from boto3.dynamodb.conditions import Key

from schemas import IncomingTask
from dynamo_client import get_dynamo_client

app = FastAPI()


@app.get("/")
async def root():
    return {"ping": "pong"}


@app.post("/todos")
async def create_todo(
        task: IncomingTask,
        dynamo_client=Depends(get_dynamo_client),
):
    created_at = int(time.time())

    new_task = {
        "content": task.content,
        "user_id": task.user_id,
        "task_id": uuid.uuid4().hex,
        "is_completed": False if task.is_completed is None else task.is_completed,
        "created_time": created_at,
        "ttl": created_at + (24 * 60 * 60),  # ttl = created_at + 24 hours
    }

    dynamo_client.put_item(
        Item=new_task
    )
    return {"task": new_task}


@app.get("/todos/{task_id}")
async def get_todo_by_id(
        task_id: str,
        dynamo_client=Depends(get_dynamo_client),
):
    response = dynamo_client.get_item(
        Key={"task_id": task_id}
    )
    item = response["Item"]
    if not item:
        raise HTTPException(
            detail="Task not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return {"task": item}


@app.get("/all-todos/{user_id}")
async def get_todos_by_user(
        user_id: str,
        dynamo_client=Depends(get_dynamo_client),
):
    response = dynamo_client.query(
        IndexName="user-index",
        KeyConditionExpression=Key("user_id").eq(user_id),
        ScanIndexForward=False,
        Limit=10,
    )
    items = response["Items"]
    return {"tasks": items}


@app.put("/todos/{task_id}")
@app.patch("/todos/{task_id}")
async def update_todo(
        task_id: str,
        task: IncomingTask,
        dynamo_client=Depends(get_dynamo_client),
):
    dynamo_client.update_item(
        Key={"task_id": task_id},
        UpdateExpression="SET content = :content, is_completed = :is_completed",
        ExpressionAttributeValues={
            ":content": task.content,
            ":is_completed": task.is_completed,
        },
        ReturnValues="ALL_NEW",
    )
    return {"updated_task_id": task_id}


@app.delete("/todos/{task_id}")
async def delete_todo(
        task_id: str,
        dynamo_client=Depends(get_dynamo_client),
):
    dynamo_client.delete_item(
        Key={"task_id": task_id}
    )
    return {"deleted_task_id": task_id}


handler = Mangum(app)  # bridge FastAPI app to AWS Lambda
