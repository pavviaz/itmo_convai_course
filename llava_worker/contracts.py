from pydantic import BaseModel, Field


class WorkerRequest(BaseModel):
    prompt: str = Field(
        title="Text input. It must contain all special seps",
    )
    img: str | None = Field(
        default=None,
        title="Telegram URL input image",
    )
    max_new_tokens: int = Field(
        default=1024,
        title="Max new generated tokens",
    )
