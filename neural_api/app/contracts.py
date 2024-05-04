from pydantic import BaseModel, Field


class DFFHelperRequest(BaseModel):
    request: str = Field(
        title="User input",
    )
    img: str | None = Field(
        default=None,
        title="Telegram URL input image",
    )


class DFFMasterRequest(BaseModel):
    llm_ctx: str = Field(
        title="Whole LLM conversation with seps"
    )
    request: str = Field(
        title="User input",
    )
    img: str | None = Field(
        default=None,
        title="Telegram URL input image",
    )
    country: str | None = Field(
        default=None,
        title="country to describe",
    )
    # nation: str | None = Field(
    #     default=None,
    #     title="nation",
    # )
