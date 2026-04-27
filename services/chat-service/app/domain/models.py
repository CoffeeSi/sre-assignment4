from dataclasses import dataclass


@dataclass
class Message:
    user_id: int
    user_name: str
    text: str
