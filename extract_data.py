from pydantic import BaseModel , Field,AnyHttpUrl
# from pydantic_extra_types.phone_numbers import PhoneNumber
from typing import Optional
import phonenumbers

class extract(BaseModel):
    """entities to be extracted are mentioned here"""
    name :Optional[str]=Field(description="the name of the sender strictly from the email content , usually present at the start of the email")
    organization:Optional[str]=Field(description="name of the orgaization or company or university strictly from the email content")
    phone: Optional[str]=Field(description="search for phone numbers , and return empty string if phonenumber is not found" , default=None)
    url:Optional[str]=Field(description="any urls mentioned in the email" ,  default=None)
    physical_Adress:Optional[str]=Field(description="search for any location names mentioned")
    financial_Data:Optional[str]=Field(description="any financial data mentioned in the email", default=None)
    attachment:bool=Field(description="search for the keyword like attachement ,attachements, attached etc")
    actionable_items:Optional[str]=Field(description="any actionable items in the email espcially check whether response is needed(e.g. meeting links , agenda ,tasks, events , assigments or reply required etc)")
    deadline:Optional[str]=Field(description="deadline mentioned in the form of present tense or future tense , or a date ,month or year, or use of tommorow or day after etc ,", default=None)
    unique_identifier:Optional[str]=Field(description="a unique identifier for the email like Customer IDs, claim numbers, loan conditions, policy numbers etc", default=None)
