import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'aspirine',
}

def describe_tables(db_config):
    connection = pymysql.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database']
    )
    cursor = connection.cursor()

    # Remaining code for fetching tables and creating statements remains the same
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    if tables:
        for (table_name,) in tables:
            cursor.execute(f"DESCRIBE {table_name}")
            description = cursor.fetchall()
            # print(f"Table: {table_name}\n")
            # print("Schema:")
            for column in description:
                # print(column)
                pass
            cursor.execute(f"SHOW CREATE TABLE {table_name}")
            create_statement = cursor.fetchone()[1]
            # print("\nCREATE TABLE statement:")
            print(create_statement)


    cursor.close()
    connection.close()

if __name__ == "__main__":
    describe_tables(DB_CONFIG)
