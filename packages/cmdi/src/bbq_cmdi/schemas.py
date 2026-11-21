from pydantic import BaseModel


class PingResult(BaseModel):
    host: str
    command: str
    exit_code: int
    output: str
