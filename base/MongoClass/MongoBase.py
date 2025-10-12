from pymongo import AsyncMongoClient
from abc import *

# CRUD 동작을 모두 정의하도록 강제하는 추상 클래스 선언
class MongoBase(metaclass=ABCMeta):
    user_id = ''
    password = ''
    uri = ''
    client = None
    data_id = None
    def __init__(self):
        return
    def login(self,userid, pw):
        # connect to collection
        self.user_id = userid
        self.password = pw
        self.uri = f"mongodb+srv://{self.user_id}:{self.password}@cluster0.a5yzzjf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        self.client = AsyncMongoClient(self.uri)
        return

    @abstractmethod
    def insert(self, data):
        return
    def getid(self):
        return
    @abstractmethod
    def find(self):
        return

    @abstractmethod
    def update(self):
        return
    @abstractmethod
    def delete(self):
        return

