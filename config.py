from dotenv import load_dotenv
import os

load_dotenv()

# user = os.environ["MYSQL_USER"]
# password = os.environ["MYSQL_PASSWORD"]
# host = os.environ["MYSQL_HOST"]
# database = os.environ["MYSQL_DATABASE"]
user = "leonux"
password = "crysis2pc"
host = "127.0.0.1"
database = "contactsdb"

DATABASE_CONNECTION_URI = f'mysql://{user}:{password}@{host}/{database}'
print(DATABASE_CONNECTION_URI)
