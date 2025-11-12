# mongoDB의 CONTENT 데이터베이스와 통신하기 위한 클래스
from base.datamodel.ModelContent import CONTENT, UNIQUE_CONTENT, SUMMARY_INFO, WEBSITE_DOMAIN
from base.MongoClass.MongoBase import MongoBase
from pymongo import AsyncMongoClient, read_concern, write_concern
from typing import List
from datetime import datetime
from copy import copy
from itertools import product
from ulid import ULID

class MongoContent(MongoBase):
    collection_name = ''
    DOCUMENT_DB = None
    COLLECTION = None
    cursor = None
    def __init__(self, collection_name):
        self.collection_name = collection_name
        return
    '''
    def login(self,userid, pw, dbip):
        # connect to collection
        self.user_id = userid
        self.password = pw
        self.uri = f"mongodb+srv://{self.user_id}:{self.password}@cluster0.a5yzzjf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        self.client = AsyncMongoClient(self.uri)
        return
    '''
    def setCollection(self, collection_name):
        self.collection_name = collection_name
        return

    def __connect__(self):
        wc = write_concern.WriteConcern(w='majority',j=True)
        rc = read_concern.ReadConcern('majority')
        self.DOCUMENT_DB = self.client.get_database("Document_DB")
        if self.collection_name == 'CONTENT':
            self.COLLECTION = self.DOCUMENT_DB.get_collection("CONTENT").with_options(write_concern=wc, read_concern=rc)
        elif self.collection_name == 'SUMMARY_INFO':
            self.COLLECTION = self.DOCUMENT_DB.get_collection("SUMMARY_INFO").with_options(write_concern=wc, read_concern=rc)
        elif self.collection_name == 'UNIQUE_CONTENT':
            self.COLLECTION = self.DOCUMENT_DB.get_collection("UNIQUE_CONTENT").with_options(write_concern=wc, read_concern=rc)
        elif self.collection_name == 'WEBSITE_DOMAIN':
            self.COLLECTION = self.DOCUMENT_DB.get_collection("WEBSITE_DOMAIN").with_options(write_concern=wc, read_concern=rc)
        else:
            raise Exception(f'{self.collection_name}은 존재하지 않는 콜렉션입니다')

    async def insert(self, data:List[dict]):
        #id 자동 입력
        for i, d in enumerate(data):
            data[i]['_id'] = ULID()
        try:
            self.__connect__()
            document_list = []
            if self.collection_name == 'CONTENT':
                #데이터 정합성 체크
                for i, d in enumerate(data):
                    document_list.append(CONTENT(**d))
            elif self.collection_name == 'SUMMARY_INFO':
                for i, d in enumerate(data):
                    document_list.append(SUMMARY_INFO(**d))
            elif self.collection_name == 'UNIQUE_CONTENT':
                for i, d in enumerate(data):
                    document_list.append(UNIQUE_CONTENT(**d))
            elif self.collection_name == 'WEBSITE_DOMAIN':
                for i, d in enumerate(data):
                    document_list.append(WEBSITE_DOMAIN(**d))
            else:
                raise Exception('정합성 체크에서 에러가 발생했습니다}')

            #insert 가능한 형태로 변환
            for i, d in enumerate(document_list):
                document_list[i] = d.dict()
            await self.COLLECTION.insert_many(document_list)


        except Exception as e:
            raise Exception("Unable to insert the document due to the following error: ", e)
        return

    async def read(self, n:int = 10):
        try:
            docs = []
            if n == -1: #-1이 입력으로 주어질 경우 전체 조회
                async for doc in self.cursor:
                    docs.append(doc)
            else:
                i = 0
                async for doc in self.cursor:
                    docs.append(doc)
                    i += 1
                    if i == n: return docs
        except Exception as e:
            raise Exception(f'read 메소드에서 에러가 발생했습니다. : {e}')
        return docs

    async def find(self, query_filter:dict={}, n:int = 10):
        try:
            self.__connect__()
            self.cursor = self.COLLECTION.find(query_filter)
            docs = await self.read(n)

        except Exception as e:
            raise Exception(f'find: 에러가 발생했습니다. : {e}')
        return docs

    async def findOne(self, query_filter:dict={}):
        try:
            self.__connect__()
            doc = await self.COLLECTION.find_one(query_filter)

        except Exception as e:
            raise Exception(f'find: 에러가 발생했습니다. : {e}')
        return doc

    async def findSorted(self, query_filter:dict={}, n:int=10, sortby:str='created_date', asc:int = -1):
        try:
            self.__connect__()
            # desc: -1, asc: 1
            self.cursor = self.COLLECTION.find(query_filter).sort(sortby, asc)
            docs = await self.read(n)

        except Exception as e:
            raise Exception(f'findLatest: 에러가 발생했습니다. : {e}')
        return docs

    async def update(self, query_filter:dict={}, update_operation:dict={}):
        try:
            self.__connect__()
            update_operation['$set']['updated_date'] = datetime.now()
            update_operation['$set']['status.latest_action'] = 'U'
            result = await self.COLLECTION.update_many(query_filter, update_operation)
        except Exception as e:
            raise Exception(f'update: 에러가 발생했습니다 : {e}')
        return result

    # 현재 콜렉션 내에서 쿼리 조건을 만족하는 데이터의 id를 반환
    async def findid(self, query_filter):
        ids = []
        try:
            self.__connect__()
            self.cursor = self.COLLECTION.find(query_filter)
            docs = await self.read(-1)
            for doc in docs:
                ids.append(doc['_id'])
        except Exception as e:
            raise Exception(f'find: 에러가 발생했습니다. : {e}')
        return ids

#삭제할 문서 대기열에 추가
    async def delete(self, query_filter:dict={}):
        try:
            self.__connect__()
            if len(query_filter)==0:
                raise Exception("쿼리 조건을 넣어주세요. 전체 데이터 삭제는 불가합니다.")

            update_operation = {'$set':{'status.latest_action':'D'}}
            await self.update(query_filter, update_operation)

            if self.collection_name == 'CONTENT':
                del_query_filter = {'status.latest_action':'D'}
                content_ids = await self.findid(del_query_filter)
                ref_colls = ['SUMMARY_INFO', 'UNIQUE_CONTENT']

                for content_id, ref_coll in product(content_ids, ref_colls):
                    ref_query_filter = {'content_id':content_id}
                    COLLECTION = self.DOCUMENT_DB.get_collection(ref_coll)
                    await COLLECTION.update_many(ref_query_filter, update_operation)

            elif self.collection_name == 'WEBSITE_DOMAIN':
                del_query_filter = {'status.latest_action': 'D'}
                website_domain_ids = await self.findid(del_query_filter)
                ref_colls = ['CONTENT']

                for website_domain_id, ref_coll in product(website_domain_ids, ref_colls):
                    ref_query_filter = {'website_domain_id': website_domain_id}
                    COLLECTION = self.DOCUMENT_DB.get_collection(ref_coll)
                    await COLLECTION.update_many(ref_query_filter, update_operation)

                tmp = copy(self.collection_name)
                self.setCollection('CONTENT')
                await self.delete(del_query_filter)
                self.collection_name = tmp

        except Exception as e:
            raise Exception(f'delete: 에러가 발생했습니다 : {e}')
        return

    #테스트용 메소드. 한 콜렉션의 모든 데이터를 삭제.
    async def delete_all(self):
        try:
            self.__connect__()
            query_filter = {}
            update_operation = {'$set':{'status.latest_action':'D'}}
            colls = ['CONTENT', 'SUMMARY_INFO', 'WEBSITE_DOMAIN', 'UNIQUE_CONTENT']
            for coll in colls:
                COLLECTION = self.DOCUMENT_DB.get_collection(coll)
                await COLLECTION.update_many(query_filter, update_operation)
        except Exception as e:
            raise Exception(f'delete_all: 에러가 발생했습니다 : {e}')
        return

    async def delete_permanent(self):
        try:
            self.__connect__()
            colls = ['CONTENT', 'UNIQUE_CONTENT', 'SUMMARY_INFO', 'WEBSITE_DOMAIN']
            query_filter = {'status.latest_action': 'D'}
            result = []
            for coll in colls:  #모든 콜렉션을 순회하면서 데이터 삭제
                COLLECTION = self.DOCUMENT_DB.get_collection(coll)
                result.append(await COLLECTION.delete_many(query_filter))
        except Exception as e:
            raise Exception(f'delete_permanent: 에러가 발생했습니다 : {e}')
        return result

    async def delete_cancel(self):
        try:
            self.__connect__()
            colls = ['CONTENT', 'UNIQUE_CONTENT', 'SUMMARY_INFO', 'WEBSITE_DOMAIN']
            query_filter = {'status.latest_action': 'D'}
            update_operation = {'$set':{'status.latest_action': 'N'}}
            result = []
            for coll in colls:
                COLLECTION = self.DOCUMENT_DB.get_collection(coll)
                result.append(await COLLECTION.update_many(query_filter, update_operation))
        except Exception as e:
            raise Exception(f'delete_cancel: 에러가 발생했습니다 : {e}')
        return result
