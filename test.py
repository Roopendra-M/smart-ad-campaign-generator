from pymongo import MongoClient

uri = "mongodb+srv://mardalaroopendra_db_user:691ZiwCtnRLgDYry@cluster0.ndobutz.mongodb.net/?appName=Cluster0"  # Replace with your connection string

try:
    client = MongoClient(uri)
    db = client.test_database

    print("Connected successfully! 🎉")
    print("Databases:", client.list_database_names())

except Exception as e:
    print("Connection failed ❌")
    print(e)
