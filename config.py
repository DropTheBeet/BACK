db = {
    'user' : 'root',
    'password' : 'test',
    'host' : 'localhost',
    'port' : 3306,
    'database' : 'beet'
}

DB_URL                = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"
JWT_SECRET_KEY        = 'SOME_SUPER_SECRET_KEY'
JWT_EXP_DELTA_SECONDS = 7 * 24 * 60 * 60

S3_BUCKET     = "test-bucket"
S3_ACCESS_KEY = "s3-access-key"
S3_SECRET_KEY = "s3-secrete-key"
S3_BUCKET_URL = f"https://s3.ap-northeast-2.amazonaws.com/{S3_BUCKET}/"
