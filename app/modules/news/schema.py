from pydantic import BaseModel, Field

class MonitorInput(BaseModel):
    topic: str = Field(min_length=3, max_length=200)
    keywords: list[str] = Field(default_factory=list, max_length=10)
    window_hours: int = Field(default=24, ge=1, le=168)
    max_articles: int = Field(default=12, ge=3, le=30)