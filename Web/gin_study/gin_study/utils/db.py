import pymysql

# 數據庫連接配置
DB_CONFIG = {
    'host': '18.180.122.148',
    'user': 'admin',
    'password': 'LCivpNcrALc6YDK',
    'database': 'my_database',  # 替換為你的數據庫名稱
    'charset': 'utf8mb4',
}

# 用戶類 ID為唯一編號請以ID進行判斷
class User:
    def __init__(self, uID, name):
        self.uID = uID
        self.name = name



# 群組消息類    消息越晚,group_message_ID越大   uID為發送者 gID為群組
class GroupMessage:
    def __init__(self, group_message_ID, message,Group_ID, uID):
        self.gmID = group_message_ID                
        self.message = message
        self.Group_ID=Group_ID
        self.uID = uID


# 連接到數據庫
def connect_db():
    return pymysql.connect(**DB_CONFIG)

# 1. 登錄檢查，返回 User 類，如果失敗返回 User(0, "")
def login_check(account, password):
    user = User(0, "")
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            sql = 'SELECT uID, name FROM User WHERE account = %s AND password = %s'
            cursor.execute(sql, (account, password))
            result = cursor.fetchone()
            if result:
                user = User(result[0], result[1])
            return user  # 返回用戶信息
    finally:
        connection.close()

# 1.1. 註冊並檢查，返回 User 類，如果註冊失敗返回 User(0, "")
def register_and_login(name, account, password):
    user = User(0, "")
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            # 先檢查賬號是否已存在
            sql = 'SELECT uID FROM User WHERE account = %s'
            cursor.execute(sql, (account,))
            result = cursor.fetchone()
            if result:
                return User(0, "")  # 如果賬號已存在，返回失敗

            # 插入新用戶數據
            sql = "INSERT INTO User (name, account, password) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, account, password))
            connection.commit()  # 提交插入操作

            # 插入成功後自動登錄
            return login_check(account, password)
    finally:
        connection.close()





# 2. 根據 uID 查找姓名
def get_name_by_uid(uID):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT name FROM User WHERE uID = %s"
            cursor.execute(sql, (uID))
            get=cursor.fetchone()
            if get:
                return get[0]
    finally:
        connection.close()

# 3. 根據 uID 查找群組，返回關於 list group_IDs about Group_ID
def get_groups_by_uid(uID):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT Group_ID FROM Group_Relation WHERE uID = %s"
            cursor.execute(sql, (uID))
            gropuIDs=[]
            get=cursor.fetchall()
            for row in get:
                gropuIDs.append(row[0])
            return gropuIDs # 返回群組列表
    finally:
        connection.close()

# 4. 根據 Group_ID 查找成員
def get_members_by_group_id(group_id):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT uID FROM Group_Relation WHERE Group_ID = %s"
            cursor.execute(sql, (group_id))
            uIDs=[]
            get=cursor.fetchall()
            for row in get:
                uIDs.append(row[0])
            return uIDs
    finally:
        connection.close()

# 5. 根據 Group_ID 查找對話記錄
def get_messages_by_group_id(group_id):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT Group_Message_ID,Message,Group_ID,uID FROM Group_message WHERE Group_ID = %s"
            cursor.execute(sql, (group_id))
            messages=[]
            get=cursor.fetchall()
            for row in get:
                
                messages.append(GroupMessage(row[0],row[1],row[2],row[2]))
            return messages  # 返回對話記錄
    finally:
        connection.close()

# 6. 根據 uID 查找父母 uid
def get_parents_uid_by_uid(uID):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            parents=[]
            # 查找父母
            sql_parents = "SELECT Parent_uID FROM ParentChild WHERE Child_uID = %s"
            cursor.execute(sql_parents, (uID))
            get = cursor.fetchall()
            for row in get:
                parents.append(row[0])
            
            return parents
    finally:
        connection.close()

# 6. 根據 uID 查找小孩 uid
def get_children_uid_by_uid(uID):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            # 查找小孩
            children=[]
            sql_children = "SELECT Child_uID FROM ParentChild WHERE Parent_uID = %s"
            cursor.execute(sql_children, (uID))
            get = cursor.fetchall()
            for row in get:
                children.append(row[0])
            return children  # 返回小孩
    finally:
        connection.close()


# 10.家長發送建立關係的請求 
def send_family_request(parent_ID:int, child_ID:int):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO family_request (parent_ID, child_ID)
                VALUES (%s, %s)
            """
            cursor.execute(sql, (parent_ID, child_ID))
            connection.commit()
            print("請求已成功發送")
    except Exception as e:
        print(f"Error: {e}")
        connection.rollback()
        return -1
    finally:
        connection.close()
