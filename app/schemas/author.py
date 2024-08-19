from pydantic import BaseModel
from typing import Optional

class Author(BaseModel):
    author_id: Optional[int] = None
    name: str
    biography: Optional[str] = None

class AuthorUpdateCurrent(BaseModel):
    name: Optional[str] = None
    biography: Optional[str] = None