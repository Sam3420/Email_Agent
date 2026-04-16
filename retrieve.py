from pydantic import BaseModel ,Field ,ValidationError 
from typing import List ,Optional , Any ,Dict

class Retrieve(BaseModel):
    maxRes:int=Field(default=0,gt=0)
    pageToken:Optional[str]
    q:Optional[str]
    labelId:List[str] = Field(default_factory="UNREAD")
    includeSpamTrash:bool=Field(default=False)
    messages:List[dict]=[]
    extracted_entities:Dict[str ,Any]=Field(default_factory=dict)
    intent_priority:Dict[str ,Any]=Field(default_factory=dict)