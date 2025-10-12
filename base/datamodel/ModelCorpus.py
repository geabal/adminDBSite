from pydantic import BaseModel, Field
from datetime import datetime
from typing import TypedDict, Union, Optional, List
class KR_CORPUS(BaseModel):
    word : str = Field(alias='_id')
    doc_frequency : int
    created_date: datetime = datetime.now()
    updated_date: datetime = datetime.now()
    def dict(self):
        d = super().model_dump()
        d['_id'] = d['word']
        del d['word']
        return d
    class Config:
        allow_population_by_field_name = True

class EN_CORPUS(BaseModel):
    word : str = Field(alias='_id')
    doc_frequency : int
    created_date: datetime = datetime.now()
    updated_date : datetime = datetime.now()

    def dict(self):
        d = super().model_dump()
        d['_id'] = d['word']
        del d['word']
        return d
    class Config:
        allow_population_by_field_name = True