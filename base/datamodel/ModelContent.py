from pydantic import BaseModel, Field
from datetime import datetime
from typing import TypedDict, Union, Optional, List
from ulid import ULID
class CONTENT(BaseModel):
    content_id: ULID = Field(alias='_id') #url 주소 사용
    website_domain_id: str = 'None'
    title: str = ''
    fulltext: List[str] = []
    description: str=''
    keyword: dict = {}
    media_URL: List[str] = []
    created_date : datetime = Field(default_factory=datetime.now)
    updated_date : datetime = Field(default_factory=datetime.now)
    published_date : Union[str, datetime]= 'None'
    meta : dict = {}
    URL : str
    status : dict = {'latest_action':'C', 'accessibility':1}

    def dict(self):
        d = super().model_dump()
        d['_id'] = d['content_id']
        del d['content_id']
        d['_id'] = str(d['_id'])
        return d
    class Config:
        allow_population_by_field_name = True

class SUMMARY_INFO(BaseModel):
    summary_id : ULID = Field(alias='_id')
    content_id : str #url과 동
    website_domain_id : str = 일'none'
    date : Union[str, datetime]= None
    created_date: datetime = Field(default_factory=datetime.now)
    updated_date: datetime = Field(default_factory=datetime.now)
    summary : str
    keyword : dict = {}
    meta : dict = {}
    status : dict = {'latest_action':'C', 'accessibility':1}

    def dict(self):
        d = super().model_dump()
        d['_id'] = d['summary_id']
        del d['summary_id']
        d['_id'] = str(d['_id'])
        return d
    class Config:
        allow_population_by_field_name = True


class UNIQUE_CONTENT(BaseModel):
    unique_content_id :ULID = Field(alias='_id')
    content_id: str
    date : Union[str, datetime] = None
    created_date: datetime = Field(default_factory=datetime.now)
    updated_date: datetime = Field(default_factory=datetime.now)
    keyword : dict = {}
    num_sim : int = 0
    sim_id : List[int] = []
    sim_rate : List[float] = []
    meta: dict = {}
    status : dict = {'latest_action':'C', 'accessibility':1}

    def dict(self):
        d = super().model_dump()
        d['_id'] = d['unique_content_id']
        del d['unique_content_id']
        d['_id'] = str(d['_id'])
        return d

    class Config:
        allow_population_by_field_name = True


class WEBSITE_DOMAIN(BaseModel):
    website_domain_id: ULID = Field(alias='_id')
    root_domain : str
    domain_name : str = ''
    domain_rank : float = 0 # 스팸 도메인일 확률 등을 포함해 계산
    domain_type : int = 0
    created_date: datetime = Field(default_factory=datetime.now)
    updated_date: datetime = Field(default_factory=datetime.now)
    meta : dict = {}
    status : dict = {'latest_action':'C', 'accessibility':1}

    def dict(self):
        d = super().model_dump()
        d['_id'] = d['website_domain_id']
        del d['website_domain_id']
        d['_id'] = str(d['_id'])
        return d

    class Config:
        allow_population_by_field_name = True

