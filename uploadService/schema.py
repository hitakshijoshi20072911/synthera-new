from pydantic import BaseModel
class UploadSchema(BaseModel):
    content_type:str
    file_name: str
