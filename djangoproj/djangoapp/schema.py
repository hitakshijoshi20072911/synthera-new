from ninja import Schema
from typing import Optional, List
from datetime import datetime
class InputSchema(Schema):
    text: str
    molecule : Optional[str]  = None
    tasks : Optional[List[str]] = None
    region : Optional[str] = None
    timeframe : Optional[int] = 5


class GetSignedUrl(Schema):
    file_name: str
    content_type : str

class ChatHistoryOut(Schema):
    timestamp: datetime 
    response : str
    file_url : str
    sources_links : List[str]
