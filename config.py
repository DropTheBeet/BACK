import time
import threading

db = {
    'user' : 'bit',
    'password' : 'test',
    'host' : '14.32.18.169',
    'port' : 3306,
    'database' : 'beet'
}


DB_URL                = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"
JWT_SECRET_KEY        = 'SOME_SUPER_SECRET_KEY'
JWT_EXP_DELTA_SECONDS = 7 * 24 * 60 * 60

S3_BUCKET     = "beetbitbucket"
S3_ACCESS_KEY = "AKIAWP6LXW45RHJWSNMS"
S3_SECRET_KEY = "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"
S3_BUCKET_URL = f"https://s3.ap-northeast-2.amazonaws.com/{S3_BUCKET}/"

def thread_run():
    print('=====', time.ctime(), '=====')
