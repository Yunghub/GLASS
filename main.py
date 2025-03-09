import os
import hashlib
import uuid
import json
from datetime import datetime

from fastapi import FastAPI

from getpass import getpass
import mysql.connector

# Creating config.yml if not existance
def start():
    global config
    try:
        with open("config.json", "r") as c:
            config = json.load(c)
    except FileNotFoundError:
        print ("Config not found, making one")
        with open("config.json","w") as c:
            json.dump({
                "Admin Password": "",
                "Admin Firstname": "",
                "Admin Lastname": "",
                "Admin Email": "",
                "Admin Phone": ""
            }, c, indent=2)
        raise Exception ("Fill in your config.json before continuing")
        exit()
        
app = FastAPI()
start()


def hash(data):
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

# Try connect to the database
try:
    db = mysql.connector.connect(
        host="node.yungcz.com",
        user="u228_onydCMakpE",
        password="vOXxzL.nI=WMgyXel@zYZ868",
        database="s228_authentication",
    )
    cursor = db.cursor()
    print ("[ GLASS ] Successfully connected to the Database")
        
except Exception as e:
    print(e)
    
# Query to make the accounts table
query = """
    CREATE TABLE IF NOT EXISTS `accounts` (
  	`username` VARCHAR(65) NOT NULL,
  	`password` LONGTEXT NOT NULL,
    `firstname` LONGTEXT NOT NULL,
    `lastname` LONGTEXT NOT NULL,
  	`email` LONGTEXT NOT NULL,
    `phone` BIGINT,
    `student` BOOLEAN NOT NULL,
    `parent` BOOLEAN NOT NULL,
    `teacher` BOOLEAN NOT NULL,
    `admin` BOOLEAN NOT NULL,
    PRIMARY KEY (`username`)
    ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
    """
cursor.execute(query)
print ("[ GLASS ] Successfully created / read the accounts table")

# Adds the default user in, if not exist
try:
    # Default Admin User
    query = "INSERT INTO accounts (username, password, firstname, lastname, email, phone, student, parent, teacher, admin) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (hash("admin"), hash(config["Admin Password"]), config["Admin Firstname"], config["Admin Lastname"], config["Admin Email"], config["Admin Phone"], False, False, False, True)
    cursor.execute(query,val)
    db.commit()
except mysql.connector.IntegrityError as e:
    print ("Already has Admin account...")

#Add default inviteCodes table
query = """
    CREATE TABLE IF NOT EXISTS `inviteCodes` (
  	`code` VARCHAR(128) NOT NULL,
    `firstname` LONGTEXT NOT NULL,
    `lastname` LONGTEXT NOT NULL,
    `student` BOOLEAN NOT NULL,
    `parent` BOOLEAN NOT NULL,
    `teacher` BOOLEAN NOT NULL,
    `admin` BOOLEAN NOT NULL,
    PRIMARY KEY (`code`)
    ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
    """
cursor.execute(query)
print ("[ GLASS ] Successfully created / read the Invite Codes table")

#Add default LessonID table
query = """
    CREATE TABLE IF NOT EXISTS `LessonID` (
  	`ID` VARCHAR(128) NOT NULL,
    `teacherID` JSON NOT NULL,
    `studentID` JSON NOT NULL,
    `date` DATETIME NOT NULL,
    PRIMARY KEY (`ID`)
    ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
    """
cursor.execute(query)
print ("[ GLASS ] Successfully created / read the LessonID table")


@app.get("/")
def read_root():
    return {"API": "Online"}

@app.post("/register/{invite_code}:{username}:{password}:{email}:{phone}")
def register(invite_code: str, username: str, password: str, email: str, phone: int):
    cursor.execute("SELECT * FROM inviteCodes WHERE code = %s", (invite_code,))
    code = cursor.fetchone()
    try:
        if code[0] == invite_code:
            firstname = code[1]
            lastname = code[2]
            student = code[3]
            parent = code[4]
            teacher = code[5]
            admin = code[6]
            userhash = hash(username)
            passhash = hash(password)
            cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
            account = cursor.fetchone()
            if account == None:
                cursor.execute("DELETE FROM inviteCodes WHERE code = %s", (invite_code,))
                query = "INSERT INTO accounts (username, password, firstname, lastname, email, phone, student, parent, teacher, admin) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = (userhash, passhash, firstname, lastname, email, phone, student, parent, teacher, admin)
                cursor.execute(query,val)
                db.commit()
                return {"username": username, "password": password, "user_id":userhash, "hashed_password": passhash}
            else:
                return {"Already Exists"}
        else:
            return {"Invite Code does not Exist"}
    except TypeError as e:
        return {"Invite Code does not Exist"}

@app.get("/login/{username}:{password}")
def login(username:str, password:str):
    userhash = hash(username)
    passhash = hash(password)
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    account = cursor.fetchone()
    print (account)
    try:
        if account[1] == passhash:
            return {"Successful"}
        else:
            return {"Failed Attempt"}
    except TypeError:
        return {"Account does not Exist"}

@app.get("/admin/{username}:{password}/invite_codes/add/{firstname}:{lastname}:{student}:{parent}:{teacher}:{admin}")
def add_code(code: str, username:str, password:str, firstname:str, lastname:str, email:str, phone:int, student:bool, parent:bool, teacher:bool, admin:bool):
    userhash = hash(username)
    passhash = hash(password)
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    account = cursor.fetchone()
    try:
        if account[1] == passhash and account[9] == True:
            try:
                query = "INSERT INTO inviteCodes (code, firstname, lastname, student, parent, teacher, admin) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                val = (code, firstname, lastname, student, parent, teacher, admin)
                cursor.execute(query,val)
                db.commit()
                return {"Successful, added!"}
            except mysql.connector.IntegrityError as e:
                return {"Code Already Exists"}
        else:
            return {"Failed Attempt"}
    except TypeError:
        return {"Account does not Exist"}

@app.get("/admin/{username}:{password}/invite_codes/remove/{invite_code}")
def remove_code_code(username: str, password: str, invite_code:str):
    userhash = hash(username)
    passhash = hash(password)
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    account = cursor.fetchone()
    try:
        if account[1] == passhash and account[9] == True:
            try:
                cursor.execute("DELETE FROM inviteCodes WHERE code = %s", (invite_code,))
                db.commit()
                return {"Removed Code"}
            except Exception as e:
                print (e)
        else:
            return {"Failed Attempt"}
    except TypeError:
        return {"Account does not Exist"}

@app.get("/admin/{username}:{password}/get_accounts")
def get_accounts(username: str, password: str):
    userhash = hash(username)
    passhash = hash(password)
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    account = cursor.fetchone()
    try:
        if account[1] == passhash and account[9] == True:
            try:
                query = "SELECT * FROM accounts"
                cursor.execute(query)
                result = cursor.fetchall()
                return {str(result)}
            except Exception as e:
                print (e)
        else:
            return {"Failed Attempt"}
    except TypeError:
        return {"Account does not Exist"}

@app.get("/admin/{username}:{password}/clear_accounts")
def clear_accounts(username: str, password: str):
    userhash = hash(username)
    passhash = hash(password)
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    account = cursor.fetchone()
    try:
        if account[1] == passhash and account[9] == True:
            try:
                cursor.execute("TRUNCATE TABLE accounts")
                db.commit()
                return {"Truncated Accounts"}
            except Exception as e:
                print (e)
        else:
            return {"Failed Attempt"}
    except TypeError:
        return {"Account does not Exist"}
    
@app.get("/admin/{username}:{password}/clear_invites")
def clear_invites(username: str, password: str):
    userhash = hash(username)
    passhash = hash(password)
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    account = cursor.fetchone()
    try:
        if account[1] == passhash and account[9] == True:
            try:
                cursor.execute("TRUNCATE TABLE inviteCodes")
                db.commit()
                return {"Truncated Accounts"}
            except Exception as e:
                print (e)
        else:
            return {"Failed Attempt"}
    except TypeError:
        return {"Account does not Exist"}

@app.get("/admin/{username}:{password}/timetables/add/{lesson_id}:{teacher_ids}:{student_ids}:{datetime}")
def add_timetable(username: str, password: str, lesson_id:str, teacher_ids:str, student_ids:str, datetime:str):
    userhash = hash(username)
    passhash = hash(password)
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    account = cursor.fetchone()
    try:
        if account[1] == passhash and account[9] == True:
            try:
                teacher_list = splitStringToList(teacher_ids)
                student_list = splitStringToList(student_ids)
                datetime = changeStringToDatetime(datetime)
                query = "INSERT INTO inviteCodes (ID, teacherID, studentID, date) VALUES (%s, %s, %s, %s)"
                val = (lesson_id, teacher_list, student_list, datetime)
                cursor.execute(query,val)
                db.commit()
                return {"Successful, added!"}
            except mysql.connector.IntegrityError as e:
                return {"Code Already Exists"}
        else:
            return {"Failed Attempt"}
    except TypeError:
        return {"Account does not Exist"}

@app.get("/admin/{username}:{password}/timetables/remove/{lesson_id}")
def remove_timetable(username: str, password: str, lesson_id:str):
    userhash = hash(username)
    passhash = hash(password)
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    account = cursor.fetchone()
    try:
        if account[1] == passhash and account[9] == True:
            try:
                cursor.execute("DELETE FROM inviteCodes WHERE ID = %s", (lesson_id,))
                db.commit()
                return {"Removed Code"}
            except Exception as e:
                print (e)
        else:
            return {"Failed Attempt"}
    except TypeError:
        return {"Account does not Exist"}


async def splitStringToList(string):
    return string.split(",")

def convertListToJSON(list):
    return json.dumps(list)
