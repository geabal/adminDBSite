from pymongo import MongoClient
#from django.conf import settings

def main():
    #user_name = settings.DB_ID
    #password = settings.DB_PASSWORD
    #ip = settings.DB_IP
    #client = MongoClient(f"mongodb://{user_name}:{password}@{ip}", 27017)
    client = MongoClient("mongodb://psjoyo86_db_user:98JMQDkN2sES5B6l@172.31.43.165", 27017)
    try:
        si = client.server_info()
        print(si)
    except Exception as e:
        print(f"에러가 발생했습니다: {e}")

main()
