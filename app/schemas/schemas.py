from pydantic import BaseModel, EmailStr, model_validator, Field
from datetime import datetime
from pydantic import ConfigDict

# class UserCreate(BaseModel):
#     pass

# class UserLogin(BaseModel): 
#     pass

# class UserResponse(BaseModel):
#     pass

class LinkCreate(BaseModel):
    url: str
    

class LinkResponse(BaseModel):
    shortcode: str
    url: str
    accessCount: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)



