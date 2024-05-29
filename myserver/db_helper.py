import hashlib
import sqlite3
import os
from typing import List, Optional, Tuple

db_PATH = './DATABASE_PATH/'
SEP = '_@#sE!p_'

def connect_database(db_name : str, db_password : str) -> Optional[sqlite3.Connection]:
    connection=None
    if not os.path.exists(db_PATH + db_name):
        connection = create_table(db_name, db_password)
    else:
        connection = check_privilege(db_name, db_password)
    return connection


def create_table(db_name : str, db_password : str) -> sqlite3.Connection:
    '''创建一个名为db_name的数据库, 在里面建一个password表, 把密码放进去, 创建memo表存数据'''

    if not os.path.exists(db_PATH):
        os.makedirs(db_PATH)

    connection = sqlite3.connect(db_PATH + db_name)
    cursor = connection.cursor()

    cursor.execute('''
                CREATE TABLE IF NOT EXISTS memo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content text,
                    lastModifyTime text,
                    title text
                );
            ''')
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS password (
                        id INTEGER PRIMARY KEY not null,
                        value text
                    );
                ''')
    connection.commit()
    # 插入密码数据
    password_md5 = hashlib.md5(db_password.encode('utf8')).hexdigest()
    # 防止sql注入
    cursor.execute('INSERT INTO password VALUES (?, ?)', (1, password_md5))

    connection.commit()

    return connection

# 验证密码是否正确
def check_privilege(db_name : str, db_password : str) -> Optional[sqlite3.Connection]:
    connection = sqlite3.connect(db_PATH+db_name)
    cursor = connection.cursor()

    password_md5 = hashlib.md5(db_password.encode('utf8')).hexdigest()

    query_result = cursor.execute("select value from password")
    password_result = query_result.fetchone()[0]

    if password_result == password_md5:
        return connection
    else:
        connection.close()
        return None



def InsertOneMemo(conn : sqlite3.Connection, data : str) -> bool:
    '''增加一条数据'''

    try:
        row_number, content, lastModifyTime, title = data.split(SEP)
        cursor = conn.cursor()

        query = 'INSERT INTO memo(content, lastModifyTime, title) VALUES (?, ?, ?)'
        cursor.execute(query, (content, lastModifyTime, title))

        # 提交事务
        conn.commit()

        print('Insert one memo succeed')
        return True
    except sqlite3.Error as e:
        # 发生错误时回滚事务
        conn.rollback()
        print(f'Error inserting memo: {e}')
        return False



def getAllMemo(conn : sqlite3.Connection) -> List[Tuple[int, str, str, str]]:
    '''获取数据库所有数据'''
    query ='select * from memo;'
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


