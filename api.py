import os
import hashlib
import uuid
import json
from datetime import datetime
import time


from getpass import getpass
import mysql.connector

from fastapi import FastAPI, Request, HTTPException
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware


# Creating config.yml if not existance
def start():a
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
        
except Error as e:
    print(e)

# Try connect to the database
try:
    attendanceDB = mysql.connector.connect(
        host="node.yungcz.com",
        user="u228_imb2mI8Lwe",
        password="x7ZZARq8lJYi1SFxtT!CP=cO",
        database="s228_attendance",
    )
    attendanceCursor = attendanceDB.cursor()
    print ("[ GLASS ] Successfully connected to the Database")
        
except Error as e:
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
    `lessonName` LONGTEXT NOT NULL,
    `teacherID` JSON NOT NULL,
    `studentID` JSON NOT NULL,
    `date` DATETIME NOT NULL,
    PRIMARY KEY (`ID`)
    ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
    """
cursor.execute(query)
print ("[ GLASS ] Successfully created / read the LessonID table")

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )
]

app = FastAPI(middleware=middleware)

@app.get("/")
def read_root():
    return {"API": "Online"}

# FastAPI route handler for registration
@app.post("/register/{invite_code}:{username}:{email}:{phone}")
def register(invite_code: str, username: str, email: str, phone: int, request: Request):
    # Get the password from the request header
    password = request.headers.get('password')
    
    # If the password is not provided, raise an HTTPException
    if password == None:
        raise HTTPException(status_code=401, detail="Password not provided")
    
    # Query the inviteCodes table for the specified invite code
    cursor.execute("SELECT * FROM inviteCodes WHERE code = %s", (invite_code,))
    
    # Fetch the resulting row from the database
    code = cursor.fetchone()
    
    # Try to register the user
    try:
        # If the invite code exists
        if code[0] == invite_code:
            # Get the user information from the inviteCodes table
            firstname = code[1]
            lastname = code[2]
            student = code[3]
            parent = code[4]
            teacher = code[5]
            admin = code[6]
            
            # Hash the username and password
            userhash = hash(username)
            passhash = hash(password)

            # Query the accounts table for the account with the specified username hash
            cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))

            # Fetch the resulting row from the database
            account = cursor.fetchone()

            
            # If the account does not exist
            if account == None:
                # Delete the invite code from the inviteCodes table
                cursor.execute("DELETE FROM inviteCodes WHERE code = %s", (invite_code,))
                
                # Insert the user information into the accounts table
                query = "INSERT INTO accounts (username, password, firstname, lastname, email, phone, student, parent, teacher, admin) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = (userhash, passhash, firstname, lastname, email, phone, student, parent, teacher, admin)
                cursor.execute(query,val)
                db.commit()
                
                # Return the username, password, user ID, and hashed password to the client
                return {"username": username, "password": password, "user_id":userhash, "hashed_password": passhash}
            # If the account already exists
            else:
                # Raise an HTTPException
                raise HTTPException(status_code=403, detail="Account already exists")
        # If the invite code does not exist
        else:
            # Raise an HTTPException
            raise HTTPException(status_code=404, detail="Invite code not found")

    #If an exception is raised during the registration process
    except TypeError as e:
        # Raise an HTTPException
        raise HTTPException(status_code=404, detail="Invite code not found.")

@app.get("/login/{username}")
def login(username:str, request: Request):
    # Get the password from the request headers
    password = request.headers.get('password')
    # Print the request headers for debugging purposes
    print (request.headers)
    # Raise an exception if the password is not provided
    if password == None:
        raise HTTPException(status_code=401, detail="Password not provided")
    # Hash the username and password
    userhash = hash(username)
    passhash = hash(password)
    # Retrieve the account with the hashed username from the database
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    account = cursor.fetchone()
    # Print the retrieved account for debugging purposes
    print (account)
    try:
        # Check if the password hash in the retrieved account matches the hashed password
        if account[1] == passhash:
            # Return a message indicating success and the account ID if the password is correct
            return {"Successful": account[0]}
        else:
            # Raise an exception if the password is incorrect
            raise HTTPException(status_code=401, detail="Password incorrect")
    except TypeError:
        # Raise an exception if a TypeError is caught (which could occur if the account is not found)
        raise HTTPException(status_code=404, detail="Account not found")

@app.post("/admin/{username}/invite_codes/add/{code}:{firstname}:{lastname}:{student}:{parent}:{teacher}:{admin}")
def add_code( username:str, request: Request, code: str, firstname:str, lastname:str, student:bool, parent:bool, teacher:bool, admin:bool):
    # Get the password from the request headers
    password = request.headers.get('password')
    # Hash the username and password
    userhash = hash(username)
    passhash = hash(password)
    # Retrieve the account with the hashed username from the database
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    account = cursor.fetchone()
    try:
        # Check if the retrieved account exists and if the password hash in the account matches the hashed password, and if the account has the admin role
        if account[1] == passhash and account[9] == True:
            try:
                # Attempt to insert a new row into the inviteCodes table in the database with the provided code, first name, last name, and role information
                query = "INSERT INTO inviteCodes (code, firstname, lastname, student, parent, teacher, admin) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                val = (code, firstname, lastname, student, parent, teacher, admin)
                cursor.execute(query,val)
                db.commit()
                return {"Successful, added!"}
            except mysql.connector.IntegrityError as e:
                # Return a message indicating that the code already exists if the insert fails due to a constraint violation
                return {"Code Already Exists"}
        else:
            # Return a message indicating a failed attempt if the account does not exist or the password is incorrect, or if the account does not have the admin role
            return {"Failed Attempt"}
    except TypeError:
        # Return a message indicating that the account does not exist if a TypeError is caught (which could occur if the account is not found)
        return {"Account does not Exist"}

@app.post("/admin/{username}/invite_codes/remove/{invite_code}")
def remove_code_code(username: str, request: Request, invite_code:str):
    # Get the password from the request header
    password = request.headers.get('password')
    
    # Hash the username and password
    userhash = hash(username)
    passhash = hash(password)
    
    # Query the accounts table for the account with the specified username hash
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    
    # Fetch the resulting row from the database
    account = cursor.fetchone()
    
    # Try to remove the invite code from the inviteCodes table
    try:
        # Check that the account exists and is an admin account
        if account[1] == passhash and account[9] == True:
            # Try to delete the row from the table
            try:
                cursor.execute("DELETE FROM inviteCodes WHERE code = %s", (invite_code,))
                
                # Commit the changes to the database
                db.commit()
                
                # Return success message
                return {"Removed Code"}
            
            # Catch any exceptions that may be thrown
            except Exception as e:
                print (e)
        
        # Return failure message if the account does not exist
    except TypeError:
        return {"Account does not Exist"}

@app.get("/admin/{username}/get_accounts")
def get_accounts(username: str, request: Request):
    password = request.headers.get('password')
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
    
@app.get("/id-to-name/{username}/{userID}")
def get_accounts(username: str, request: Request, userID: str):
    password = request.headers.get('password')
    userhash = hash(username)
    passhash = hash(password)
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    account = cursor.fetchone()
    print (account)
    try:
        if account[1] == passhash:
            try:
                query = "SELECT * FROM accounts WHERE username = %s"
                cursor.execute(query,(userID,))
                result = cursor.fetchone()
                print(result)
                return {"firstname": result[2], "lastname": result[3]}
            except Exception as e:
                print (e)
        else:
            return {"Failed Attempt"}
    except TypeError:
        return {"Account does not Exist"}

@app.get("/admin/{username}/clear_accounts")
def clear_accounts(username: str, request: Request):
    password = request.headers.get('password')
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
    
@app.get("/admin/{username}/clear_invites")
def clear_invites(username: str, request: Request):
    password = request.headers.get('password')
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

@app.get("/teacher/{username}/timetables/add/{lesson_name}:{teacher_id}:{student_id}/{datetime}")
def add_timetable(username: str, request: Request, lesson_name:str, teacher_id:str, student_id:str, datetime:str):
    # Get the password from the request headers
    password = request.headers.get('password')
    # Hash the username and password
    userhash = hash(username)
    passhash = hash(password)
    # Retrieve the account with the hashed username from the database
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    account = cursor.fetchone()
    # Print the retrieved account for debugging purposes
    print (account)
    try:
        # Check if the retrieved account exists and if the password hash in the account matches the hashed password, and if the account has the admin role
        if account[1] == passhash and account[9] == True:
            try:
                # Split the student_id and teacher_id into lists of IDs
                student_list = student_id.split(",")
                teacher_list = teacher_id.split(",")
                # Initialize dictionaries for storing hashed student and teacher IDs
                studentdict = {"id": []}
                teacherdict = {"id": []}
                # Hash the lesson ID using the datetime, student_id, and teacher_id
                lesson_id = hash(datetime+student_id+teacher_id)
                # Loop through the list of student IDs
                for i in range (0, len(student_list)):
                    # Hash the current student ID
                    studentI = hash(student_list[i])
                    # Retrieve the account with the hashed student ID from the database
                    cursor.execute("SELECT * FROM accounts WHERE username = %s", (studentI,))
                    student = cursor.fetchone()
                    # Print the retrieved student account for debugging purposes
                    print (student)
                    # If the student account does not exist, return a message indicating that the student ID does not exist
                    if student == None:
                        return {"Student ID does not exist"}
                    else:
                        # Append the hashed student ID to the studentdict
                        studentdict["id"].append(studentI)
                # Loop through the list of teacher IDs
                for i in range (0, len(teacher_list)):
                    # Hash the current teacher ID
                    teacherI = hash(teacher_list[i])
                                        # Retrieve the account with the hashed teacher ID from the database
                    cursor.execute("SELECT * FROM accounts WHERE username = %s", (teacherI,))
                    teacher = cursor.fetchone()
                    # If the teacher account does not exist, return a message indicating that the teacher ID does not exist
                    if teacher == None:
                        return {"Teacher ID does not exist"}
                    else:
                        # Append the hashed teacher ID to the teacherdict
                        teacherdict["id"].append(teacherI)
                # Convert the studentdict and teacherdict to JSON strings
                student_ids = json.dumps(studentdict)
                teacher_ids = json.dumps(teacherdict)
                # Insert a new row into the LessonID table in the database with the hashed lesson ID, lesson name, hashed teacher IDs, hashed student IDs, and datetime
                query = "INSERT INTO LessonID (ID, lessonName, teacherID, studentID, date) VALUES (%s, %s, %s, %s, %s)"
                val = (lesson_id, lesson_name, teacher_ids, student_ids, datetime)
                cursor.execute(query,val)
                db.commit()
                # Create a new table in the attendance database with the name of the hashed lesson ID
                query = "CREATE TABLE " + lesson_id + " (ID VARCHAR(255), attendance VARCHAR(255))"
                attendanceCursor.execute(query)
                # Loop through the list of student IDs
                for i in range (0, len(student_list)):
                    # Insert a new row into the new table in the attendance database with the hashed student ID and an attendance status of "Absent"
                    query = "INSERT INTO " + lesson_id + " (ID, attendance) VALUES (%s, %s)"
                    val = (student[i], "Absent")
                    attendanceCursor.execute(query,val)
                attendanceDB.commit()
                # Return a message indicating that the timetable was successfully added and the hashed lesson ID
                return {f"Successful, added! {lesson_id}"}
            except mysql.connector.IntegrityError as e:
                # Return the error message if an IntegrityError occurs
                return {e}
        else:
            # Return a message indicating a failed attempt if the account does not exist or the password is incorrect
            return {"Failed Attempt"}
    except Exception as e:
        # Print the error message for debugging purposes
        print (e)
        # Return a message indicating that the account does not exist
        return {"Account does not Exist"}
        

@app.get("/admin/{username}/timetables/remove/{lesson_id}")
def remove_timetable(
    username: str,  # The username of the admin
    request: Request,  # A request object
    lesson_id: str  # The id of the lesson to remove
    ):
    password = request.headers.get('password')  # Get the password from the request headers
    userhash = hash(username)  # Hash the username
    passhash = hash(password)  # Hash the password

    # Get the account associated with the given username
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    account = cursor.fetchone()
    
    try:
        # If the password and admin status of the account match the provided password and admin status
        if account[1] == passhash and account[9] == True:
            try:
                # Remove the lesson with the given id from the database
                cursor.execute("DELETE FROM LessonID WHERE ID = %s", (lesson_id,))
                db.commit()

                # Drop the attendance table for the lesson from the database
                attendanceCursor.execute("DROP TABLE " + lesson_id)
                attendanceDB.commit()
                
                # Return a success message
                return {"Removed Code"}
            except Exception as e:
                # If there is an error, print the error and return a failed message
                print (e)
                return {"Failed Attempt"}
        else:
            # Return a failed message if the provided password and/or admin status are incorrect
            return {"Failed Attempt"}
    except TypeError:
        # Return a message indicating that the account does not exist
        return {"Account does not Exist"}



@app.get("/self/{username}/attendance/id/{lesson_id}")
def get_attendance(username: str, request: Request, lesson_id:str):
    password = request.headers.get('password')
    userhash = hash(username)
    passhash = hash(password)
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    account = cursor.fetchone()
    try:
        if account[1] == passhash:
            try:
                attendanceCursor.execute("SELECT * FROM " + lesson_id + " WHERE ID = %s", (userhash,))
                attendance = attendanceCursor.fetchone()
                return {"Attendance": attendance[1]}
            except Exception as e:
                print (e)
        else:
            return {"Failed Attempt"}
    except TypeError:
        return {"Account does not Exist"}



@app.get("/self/{username}/timetables/")
def get_timetables(username: str, request: Request):
    # Get the password from the request headers
    password = request.headers.get('password')
    # Hash the username and password
    userhash = hash(username)
    passhash = hash(password)
    # Retrieve the account with the hashed username from the database
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    account = cursor.fetchone()
    try:
        # Check if the password hash in the retrieved account matches the hashed password
        if account[1] == passhash:
            try:
                # Retrieve all the lessons in which the user with the hashed username is a student
                cursor.execute("SELECT * FROM LessonID WHERE studentID LIKE %s", ('%"' + userhash + '"%',))
                lessons = cursor.fetchall()
                # Return the retrieved lessons
                return {"Lessons": lessons}
            except Exception as e:
                # Print the error message for debugging purposes
                print (e)
        else:
            # Return a message indicating a failed attempt if the password is incorrect
            return {"Failed Attempt"}
    except TypeError:
        # Return a message indicating that the account does not exist if a TypeError occurs
        return {"Account does not Exist"}


@app.get("/self/{username}/timetables/formatted/")
def get_timetables(username: str, request: Request):
    password = request.headers.get('password')
    userhash = hash(username)
    passhash = hash(password)
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    account = cursor.fetchone()
    try:
        if account[1] == passhash:
            try:
                cursor.execute("SELECT * FROM LessonID WHERE studentID LIKE %s", ('%"' + userhash + '"%',))
                lessons = cursor.fetchall()
                print (type(lessons))
                print (lessons)
                # Turn ids into names
                
                for i in range (len(lessons)):
                    # Convert lessons[i][2] into a JSON
                    jsonTeachersNames = json.loads(lessons[i][2])
                    jsonTeachersNames = jsonTeachersNames["id"]
                    names = []
                    print ("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", jsonTeachersNames)
                    for j in range (len(jsonTeachersNames)):
                        cursor.execute("SELECT * FROM accounts WHERE username = %s", (jsonTeachersNames[j],))
                        account = cursor.fetchone()
                        names.append([account[2], account[3]])
                    lessons[i] = [lessons[i][0], lessons[i][1], names, lessons[i][3], lessons[i][4]]
                    jsonStudentsNames = json.loads(lessons[i][3])
                    jsonStudentsNames = jsonStudentsNames["id"]
                    names = []
                    for j in range (len(jsonStudentsNames)):
                        cursor.execute("SELECT * FROM accounts WHERE username = %s", (jsonStudentsNames[j],))
                        account = cursor.fetchone()
                        names.append([account[2], account[3]])
                    lessons[i] = [lessons[i][0], lessons[i][1], lessons[i][2], names, lessons[i][4]]
                return {"Lessons": lessons}

            except Exception as e:
                print (e)
        else:
            return {"Failed Attempt"}
    except TypeError:
        return {"Account does not Exist"}
    
# Calculates the attendance for a lesson and returns it as a percentage
@app.get("/self/{username}/attendance/percent/")
def get_attendance(username: str, request: Request):
    password = request.headers.get('password')
    userhash = hash(username)
    passhash = hash(password)
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    account = cursor.fetchone()
    try:
        if account[1] == passhash:
            try:
                cursor.execute("SELECT * FROM LessonID")
                lessons = cursor.fetchall()
                print (lessons)
                attendanceValue = 0
                lessonsArr = []
                for i in range (len(lessons)):
                    lessonsArr.append(lessons[i][0])
                    
                print ("ARRAY", lessonsArr)
                for i in range(0,len(lessonsArr)):
                    print ("Loop", i, lessonsArr[i])
                    attendanceCursor.execute("SELECT * FROM " + lessonsArr[i] + " WHERE ID = %s", (userhash,))
                    attendance = attendanceCursor.fetchone()
                    print ("attendance", attendance)
                    if attendance == None:
                        pass
                    elif attendance[1] == "Present":
                        attendanceValue += 1
                return {"Attendance": attendanceValue*100/len(lessonsArr)}
            except Exception as e:
                print (e)
        else:
            return {"Failed Attempt"}
    except TypeError:
        return {"Account does not Exist"}
    
    
@app.get("/self/{username}/timetables/")
def get_timetables(username: str, request: Request):
    password = request.headers.get('password')
    userhash = hash(username)
    passhash = hash(password)
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    account = cursor.fetchone()
    try:
        if account[1] == passhash:
            try:
                cursor.execute("SELECT * FROM LessonID WHERE studentID LIKE %s AND date > %s", ('%"' + userhash + '"%', datetime.now()))
                lessons = cursor.fetchall()
                return {"Lessons": lessons}
            except Exception as e:
                print (e)
        else:
            return {"Failed Attempt"}
    except TypeError:
        return {"Account does not Exist"}


@app.get("/self/{username}/timetables/coming/formatted/")
def get_timetables(username: str, request: Request):
    password = request.headers.get('password')
    userhash = hash(username)
    passhash = hash(password)
    time.sleep(0.1)
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    account = cursor.fetchone()
    try:
        if account[1] == passhash:
            try:
                cursor.execute("SELECT * FROM LessonID WHERE studentID LIKE %s AND date > %s ORDER BY date", ('%"' + userhash + '"%', datetime.now()))
                lessons = cursor.fetchall()
                print (type(lessons))
                print (lessons)
                # Turn ids into names
                
                for i in range (len(lessons)):
                    # Convert lessons[i][2] into a JSON
                    jsonTeachersNames = json.loads(lessons[i][2])
                    jsonTeachersNames = jsonTeachersNames["id"]
                    names = []
                    print ("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", jsonTeachersNames)
                    for j in range (len(jsonTeachersNames)):
                        cursor.execute("SELECT * FROM accounts WHERE username = %s", (jsonTeachersNames[j],))
                        account = cursor.fetchone()
                        names.append([account[2], account[3]])
                    lessons[i] = [lessons[i][0], lessons[i][1], names, lessons[i][3], lessons[i][4]]
                    jsonStudentsNames = json.loads(lessons[i][3])
                    jsonStudentsNames = jsonStudentsNames["id"]
                    names = []
                    for j in range (len(jsonStudentsNames)):
                        cursor.execute("SELECT * FROM accounts WHERE username = %s", (jsonStudentsNames[j],))
                        account = cursor.fetchone()
                        names.append([account[2], account[3]])
                    lessons[i] = [lessons[i][0], lessons[i][1], lessons[i][2], names, lessons[i][4]]
                return {"Lessons": lessons}

            except Exception as e:
                print (e)
        else:
            return {"Failed Attempt"}
    except TypeError:
        return {"Account does not Exist"}


@app.get("/other/{username}/{otherUsername}/attendance/id/{lesson_id}")
def get_attendance(username: str, otherUsername:str, request: Request, lesson_id:str):
    password = request.headers.get('password')
    userhash = hash(username)
    passhash = hash(password)
    otherhash = hash(otherUsername)
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    account = cursor.fetchone()
    try:
        if account[1] == passhash:
            if account[9] == True or account[8] == True: # If the user is an admin or a teacher
                try:
                    attendanceCursor.execute("SELECT * FROM " + lesson_id + " WHERE ID = %s", (otherhash,))
                    attendance = attendanceCursor.fetchone()
                    return {"Attendance": attendance[1]}
                except Exception as e:
                    print (e)
            else:
                return {"Failed Attempt"}
        else:
            return {"Failed Attempt"}
    except TypeError:
        return {"Account does not Exist"}

# Calculates the attendance for a lesson and returns it as a percentage
@app.get("/other/{username}/{otherUsername}/attendance/percent/")
def get_attendance(username: str, otherUsername:str, request: Request):
    password = request.headers.get('password')
    userhash = hash(username)
    passhash = hash(password)
    otherhash = hash(otherUsername)
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    account = cursor.fetchone()
    try:
        if account[1] == passhash:
            try:
                cursor.execute("SELECT * FROM LessonID")
                lessons = cursor.fetchall()
                print (lessons)
                attendanceValue = 0
                lessonsArr = []
                for i in range (len(lessons)):
                    lessonsArr.append(lessons[i][0])
                for lesson in lessonsArr:
                    print (lesson)
                    attendanceCursor.execute("SELECT * FROM " + lesson + " WHERE ID = %s", (otherhash,))
                    attendance = attendanceCursor.fetchone()
                    if attendance == None:
                        pass
                    elif attendance[1] == "Present":
                        attendanceValue += 1
                return {"Attendance": attendanceValue/len(lessons)}
            except Exception as e:
                print (e)
        else:
            return {"Failed Attempt"}
    except TypeError:
        return {"Account does not Exist"}
    
@app.get("/teacher/{username}/attendance/mark/{otherID}/{lesson_id}/{attendanceCode}")
def mark_attendance(username: str, otherID:str, request: Request, lesson_id:str, attendanceCode:str):
    # Get the password from the request headers
    password = request.headers.get('password')
    # Hash the username and password
    userhash = hash(username)
    passhash = hash(password)
    # Retrieve the account with the hashed username from the database
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    account = cursor.fetchone()
    try:
        # Check if the password hash in the retrieved account matches the hashed password
        if account[1] == passhash:
            # Check if the user is a teacher or an admin
            if account[8] == True or account[9] == True: 
                try:
                    # Retrieve the attendance record for the other user in the specified lesson from the attendance database
                    attendanceCursor.execute("SELECT * FROM " + lesson_id + " WHERE ID = %s",(otherID,))
                    attendance = attendanceCursor.fetchone()
                    # If the attendance record does not exist, insert a new row into the attendance table with the other user's hashed ID and the specified attendance code
                    if attendance == None:
                        attendanceCursor.execute("INSERT INTO " + lesson_id + " (ID, attendance) VALUES (%s, %s)", (otherID, attendanceCode))
                        attendanceDB.commit()
                        # Return the attendance record
                        return {"Attendance": attendance}
                    else:
                        # Update the attendance record for the other user in the specified lesson with the specified attendance code
                        attendanceCursor.execute("UPDATE " + lesson_id + " SET attendance = %s WHERE ID = %s", (attendanceCode, otherID))
                        attendanceDB.commit()
                        # Return the attendance record
                        return {"Attendance": attendance}
                except Exception as e:
                    # Print the error message for debugging purposes
                    print (e)
            else:
                # Return a message indicating a failed attempt if the user is not a teacher or an admin
                return {"Failed Attempt"}
        else:
            # Return a message indicating a failed attempt if the password is incorrect
            return {"Failed Attempt"}
    except TypeError:
        # Return a message indicating that the account does not exist if a TypeError occurs
        return {"Account does not Exist"}


# Gets attendance of everyone in a lesson
@app.get("/teacher/{username}/attendance/{lesson_id}")
def get_attendance(username: str, request: Request, lesson_id:str):
    # Get the password from the request header
    password = request.headers.get('password')
    # Hash the username and password for safe comparison in database
    userhash = hash(username)
    passhash = hash(password)
    # Get the account of the user with the given username
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    account = cursor.fetchone()
    
    # Check if the account exists
    try:
        # Check if the provided password matches the hashed password in the database
        if account[1] == passhash:
            # Check if the user is a teacher (either a regular teacher or an admin)
            if account[8] == True or account[9] == True: 
                # Try to fetch the attendance of the specified lesson
                try:
                    attendanceCursor.execute("SELECT * FROM " + lesson_id)
                    attendance = attendanceCursor.fetchall()
                    # Return the attendance as a dictionary
                    return {"Attendance": attendance}
                except Exception as e:
                    return {"Failed Attempt"}
            else:
                return {"Failed Attempt"}
        else:
            return {"Failed Attempt"}
    except TypeError:
        return {"Account does not Exist"}


@app.get("/teacher/{username}/attendance/{lesson_id}/{otherID}")
def get_attendance(username: str, request: Request, lesson_id:str, otherID:str):
    password = request.headers.get('password')
    userhash = hash(username)
    passhash = hash(password)
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    account = cursor.fetchone()
    try:
        if account[1] == passhash:
            if account[8] == True or account[9] == True: # If the user is a teacher
                try:
                    attendanceCursor.execute("SELECT * FROM " + lesson_id + " WHERE ID = %s", (otherID,))
                    attendance = attendanceCursor.fetchone()
                    return {"Attendance": attendance}
                except Exception as e:
                    print (e)
            else:
                return {"Failed Attempt"}
        else:
            return {"Failed Attempt"}
    except TypeError:
        return {"Account does not Exist"}

@app.get("/teacher/{username}/timetables/")
def get_timetables(username: str, request: Request):
    # Get the password from the request headers
    password = request.headers.get('password')
    # Hash the username and password
    userhash = hash(username)
    passhash = hash(password)
    # Retrieve the account with the hashed username from the database
    cursor.execute("SELECT * FROM accounts WHERE username = %s", (userhash,))
    account = cursor.fetchone()
    try:
        # Check if the password hash in the retrieved account matches the hashed password
        if account[1] == passhash:
            try:
                # Retrieve the lesson records for the user from the database
                cursor.execute(f"SELECT * FROM LessonID WHERE teacherID LIKE '%{userhash}%'")
                lessons = cursor.fetchall()
                # Return the lesson records
                return {"Lessons": lessons}
            except Exception as e:
                # Print the error message for debugging purposes
                print (e)
        else:
            # Return a message indicating a failed attempt if the password is incorrect
            return {"Failed Attempt"}
    except TypeError:
        # Return a message indicating that the account does not exist if a TypeError occurs
        return {"Account does not Exist"}

    

from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
