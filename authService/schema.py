from pydantic import BaseModel
class SignupSchema(BaseModel):
    email: str
    username: str
    password: str
