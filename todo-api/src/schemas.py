from pydantic import BaseModel


class IncomingTask(BaseModel):
    content: str
    user_id: str | None
    is_completed: bool | None
