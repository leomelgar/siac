from dotenv import load_dotenv
import os

load_dotenv()

# user = os.environ["MYSQL_USER"]
# password = os.environ["MYSQL_PASSWORD"]
# host = os.environ["MYSQL_HOST"]
# database = os.environ["MYSQL_DATABASE"]
SECRET_KEY = os.environ.get('SECRET_KEY', 'sisPruebaV1')
user = "leonux"
password = "crysis2pc"
host = "127.0.0.1"
database = "siac_2_db"

DATABASE_CONNECTION_URI = f'mysql+pymysql://{user}:{password}@{host}/{database}'
print(DATABASE_CONNECTION_URI)
