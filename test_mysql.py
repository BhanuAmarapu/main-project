import pymysql

try:
    # Connect to MySQL Server (no db selected yet)
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='Bhanu@2004',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    with connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS cloud_dedup")
        print("Successfully connected to MySQL and ensured 'cloud_dedup' database exists!")
        
    connection.close()

except Exception as e:
    print(f"Error connecting to MySQL: {e}")
