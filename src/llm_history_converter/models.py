from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Message:
    author: str
    text: str
    sent_at: datetime


@dataclass
class Conversation:
    id: str
    title: str
    source: str
    created_at: datetime
    updated_at: datetime
    messages: list[Message] = field(default_factory=list)
    summary: str | None = None