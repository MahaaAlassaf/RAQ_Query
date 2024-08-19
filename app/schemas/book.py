from pydantic import BaseModel
from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.author import Author
from typing import List, Optional

class Book(BaseModel):
    title: str
    subtitle: Optional[str] = None
    genre: Optional[str] = None
    published_year: Optional[int] = None
    description: Optional[str] = None
    average_rating: Optional[float] = None
    num_pages: Optional[int] = None
    ratings_count: Optional[int] = None
    thumbnail: Optional[str] = None
    author_id: Optional[int] = None

class BookCreate(BaseModel):
    title: str
    subtitle: Optional[str] = None
    thumbnail: Optional[str] = None
    genre: Optional[str] = None
    published_year: Optional[int] = None
    description: Optional[str] = None
    average_rating: Optional[float] = None
    num_pages: Optional[int] = None
    ratings_count: Optional[int] = None
    authors: List[Author] = Field(default_factory=list)

class BookUpdateCurrent(BaseModel):
    title: Optional[str] = None
    author_id: Optional[str] = None
    genre: Optional[str] = None
    description: Optional[str] = None
    year: Optional[int] = None