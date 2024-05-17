import os
import sys
import pytest
from dotenv import load_dotenv
from provider.client import ADBSClient

load_dotenv()



#Testing Wallet and Config Dir Setup
# def test_wallet_and_config_dir_setup():
#     wallet_location = os.getenv("ORACLE_WALLET_DIR")
#     config_location = os.getenv("ORACLE_CONFIG_DIR")
#     wallet_files = os.listdir(wallet_location)
#     config_files = os.listdir(config_location)
#     assert 'cwallet.sso' in wallet_files
#     assert 'tnsnames.ora' in config_files

#Test End to End Functionality
def test_end_to_end():

    #Create a DB Connection
    dsn = os.getenv("ORACLEADB_DSN")
    user = os.getenv("ORACLEADB_USER")
    password = os.getenv("ORACLEADB_PASSWORD")
    wallet_dir = os.getenv("ORACLEADB_WALLET_DIR")
    wallet_password = os.getenv("ORACLEADB_WALLET_PASSWORD")
    fts_columns = os.getenv("ORACLEADB_FTS_COLUMN_LIST")
    table_name = os.getenv("ORACLEADB_TABLE_NAME")
    auto_index_fts_columns = os.getenv("ORACLEADB_AUTO_INDEX_FTS_COLUMNS")

    print(" =========== " + dsn)

    create_table_sql = """
            CREATE TABLE EMPLOYEE (
                EMPLOYEE_ID NUMBER PRIMARY KEY,
                FIRST_NAME VARCHAR2(50),
                LAST_NAME VARCHAR2(50),
                EMPLOYEE_REVIEWS VARCHAR2(500),
                TECHNICAL_FEEDBACK VARCHAR2 (500)
            )
    """

    # SQL script to insert data into the EMPLOYEE table
    insert_data_sql = """
        INSERT INTO EMPLOYEE (EMPLOYEE_ID, FIRST_NAME, LAST_NAME, EMPLOYEE_REVIEWS, TECHNICAL_FEEDBACK)
        VALUES (:employee_id, :first_name, :last_name, :employee_reviews, :technical_feedback)
    """

    client = ADBSClient(
                        user=user, 
                        password=password, 
                        dsn=dsn,
                        wallet_dir=wallet_dir, 
                        wallet_password=wallet_password,
                        fts_columns = fts_columns,
                        table_name = table_name,
                        auto_index_fts_columns = False #as manually indexing later, as table needs needs to be made first (this is for testing only)
            )
    
    connection = client.get_connection()

    cursor = connection.cursor()

    # # Execute the create table SQL
    cursor.execute(create_table_sql)
    
    # Insert data into the EMPLOYEE table
    data_to_insert = [
        (1, 'John', 'Doe', 'Great employee, highly skilled and dedicated.', 'An elegant python Coder'),
        (2, 'Jane', 'Smith', 'Needs improvement in communication skills.', 'Can code in Java with her eyes closed'),
        (3, 'Michael', 'Johnson', 'Consistently meets deadlines and delivers quality work.', 'Eats ElasticSearch for Breakfast'),
        (4, 'Emily', 'Williams', 'Very creative and brings innovative ideas to the team.', 'He makes Python look like english'),
        (5, 'David', 'Brown', 'Excellent team player, always willing to help others.', 'Makes AI look less intelligent when he codes')
    ]

    cursor.executemany(insert_data_sql, data_to_insert)

    connection.commit()

    client._create_index_configuration()

    for column in client.fts_columns:
        client._prepare_fts_index(column)

    query = "I want to talk to people who are very skilled and help others and can also understand ElasticSearch"

    response = client.search(query)

    expected_response = [
        {'EMPLOYEE_ID': 1, 'FIRST_NAME': 'John', 'LAST_NAME': 'Doe', 'EMPLOYEE_REVIEWS': 'Great employee, highly skilled and dedicated.', 'TECHNICAL_FEEDBACK': 'An elegant python Coder'}, 
        {'EMPLOYEE_ID': 2, 'FIRST_NAME': 'Jane', 'LAST_NAME': 'Smith', 'EMPLOYEE_REVIEWS': 'Needs improvement in communication skills.', 'TECHNICAL_FEEDBACK': 'Can code in Java with her eyes closed'}, 
        {'EMPLOYEE_ID': 3, 'FIRST_NAME': 'Michael', 'LAST_NAME': 'Johnson', 'EMPLOYEE_REVIEWS': 'Consistently meets deadlines and delivers quality work.', 'TECHNICAL_FEEDBACK': 'Eats ElasticSearch for Breakfast'}, 
        {'EMPLOYEE_ID': 5, 'FIRST_NAME': 'David', 'LAST_NAME': 'Brown', 'EMPLOYEE_REVIEWS': 'Excellent team player, always willing to help others.', 'TECHNICAL_FEEDBACK': 'Makes AI look less intelligent when he codes'}
    ]

    assert response == expected_response

