from typing import Any, List
from datetime import datetime
from pydantic import BaseModel
from datetime import datetime

# Api Model
class ApiCallCreate(BaseModel):
    endpoint: str
    parameters: str
    result: str

# Contact model
class ContactCreateSchema(BaseModel):
    email: str
    firstname: str
    lastname: str
    phone: str
    website: str
    estadoclickup: str = ""

class ContactBodySchema(BaseModel):
    archived: bool
    archived_at: datetime
    associations: dict
    created_at: datetime
    id: str
    properties: dict
    properties_with_history: dict
    updated_at: datetime