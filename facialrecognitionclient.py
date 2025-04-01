import tkinter as tk
from tkinter.ttk import *
from PIL import Image, ImageTk
import requests
import datetime
import json
import camera

# Import tkinter messagebox
import tkinter.messagebox as tkMessageBox

class textClass():
    def __init__(self, text, x, y, size, colour, font):
        self.text = text
        self.x = x
        self.y = y
        self.size = size
        self.colour = colour
        self.font = font

    def create(self):
        self.label = tk.Label(window, text=self.text, font=("Poppins", self.size), fg=self.colour, bg="#000000")
        self.label.place(x=self.x, y=self.y, anchor="center")

class buttonClass():
    def __init__(self, text, x, y, size, colour, font, imageURL, command):
        self.text = text
        self.x = x
        self.y = y
        self.size = size
        self.colour = colour
        self.font = font
        self.imageURL = imageURL
        self.command = command

    def create(self):
        self.buttonPic = tk.PhotoImage(file=self.imageURL)
        self.button = tk.Button(window, text=self.text, font=("Poppins", self.size), fg=self.colour, bg="#000000", activebackground="#000000", image=self.buttonPic, borderwidth=0, highlightthickness=0, command=self.command)
        self.button.image = self.buttonPic
        self.button.place(x=self.x, y=self.y, anchor="center")

    def destroy(self):
        self.button.destroy()


selectedLessonID = []

# Create the main window
window = tk.Tk()
window.geometry("1600x1000")
window.title("GLASS Facial Recognition Client")
# Set icon image
window.iconbitmap("src/images/GLogo.ico")

# Set the background image
image = tk.PhotoImage(file="src/images/menubg.png")
background_label = tk.Label(image=image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)


def takePicture(username, passW, id):
    facial = camera.facialRecognition(username, passW, selectedLessonID)
    facial.takePicture(id)

def editPhoto(username, passW, selectedLessonID, buttonStartClient, buttonEditPhoto, homeButton, text, text2):

    # Destroy the start client button
    buttonStartClient.destroy()
    # Destroy the edit photo button
    buttonEditPhoto.destroy()
    # Destroy the home button
    homeButton.destroy()

    text2.configure(text="", font=("Poppins", 1))


    # Change background to timetableBackground.png
    image = tk.PhotoImage(file="src/images/timetablebg.png")
    background_label.configure(image=image)
    background_label.image = image

    print (selectedLessonID)
    studentString = selectedLessonID[3]
    # Turn the student string into JSON
    studentJSON = json.loads(studentString)
    studentList = studentJSON["id"]
    print (studentList)
    studentListString = ""
    for i in range (len(studentList)):
        id = studentList[i]

        url = f"https://api.yungcz.com/id-to-name/{username}/{id}"

        header = {"password": passW}
        x = requests.get(url, headers = header)
        # Get JSON data
        x = x.json()

        print (x)

        # Get the name
        firstname = x["firstname"]
        lastname = x["lastname"]

        studentListString += firstname + " " + lastname + "\n"

        buttonPic = tk.PhotoImage(file="src/images/cameraButton.png")
        button = tk.Button(window, image = buttonPic, bg = "black", activebackground="black", borderwidth=0, command=lambda i=i: takePicture(username, passW, studentList[i]))
        button.image = buttonPic
        button.place(x=1300, y=325 + (i * 100), anchor="center")

    text.configure(text=studentListString, font=("Poppins", 40))
    text.place(x=300, y=285, anchor="nw")

    buttonPic = tk.PhotoImage(file="src/images/homeButton.png")
    homeButton = tk.Button(window, image = buttonPic, bg = "black", activebackground="black", borderwidth=0, command=lambda button = "" : menu(id, username, passW, homeButton, button, text, text2))
    homeButton.image = buttonPic
    homeButton.place(x=800, y=935, anchor="center")


def manualAttendance(id, username, passW, text, text2, time, settingsButton, logoutButton, facialRegisterButton, manualRegisterButton, timetablesButton, modifyClassButton):

    if len(selectedLessonID) == 0:
        # Show error message using tkinter warning
        text.configure(text="Please select a lesson in timetables\n before continuing", font=("Poppins", 50))
        text.place (x=800, y=550, anchor="center")
        text2.configure(text="GLASS", font=("Poppins", 100))
        text2.place (x=800, y=150, anchor="center")
        time.destroy()
        settingsButton.destroy()
        logoutButton.destroy()
        facialRegisterButton.destroy()
        manualRegisterButton.destroy()
        timetablesButton.destroy()
        modifyClassButton.destroy()

        buttonPic = tk.PhotoImage(file="src/images/homeButton.png")
        homeButton = tk.Button(window, image = buttonPic, bg = "black", activebackground="black", borderwidth=0, command=lambda button = "": menu(id, username, passW, homeButton, button, text, text2))
        homeButton.image = buttonPic
        homeButton.place(x=800, y=900, anchor="center")

    else:
        text2.configure(text="", font=("Poppins", 1))

        time.destroy()
        settingsButton.destroy()
        logoutButton.destroy()
        facialRegisterButton.destroy()
        manualRegisterButton.destroy()
        timetablesButton.destroy()
        modifyClassButton.destroy()

        # Change background to timetableBackground.png
        image = tk.PhotoImage(file="src/images/timetablebg.png")
        background_label.configure(image=image)
        background_label.image = image

        print (selectedLessonID)
        studentString = selectedLessonID[3]
        # Turn the student string into JSON
        studentJSON = json.loads(studentString)
        studentList = studentJSON["id"]
        print (studentList)
        studentListString = ""
        for i in range (len(studentList)):
            id = studentList[i]

            url = f"https://api.yungcz.com/id-to-name/{username}/{id}"

            header = {"password": passW}
            x = requests.get(url, headers = header)
            # Get JSON data
            x = x.json()

            # Get the name
            firstname = x["firstname"]
            lastname = x["lastname"]

            studentListString += firstname + " " + lastname + "\n"

            url = f"https://api.yungcz.com/teacher/{username}/attendance/{selectedLessonID[0]}/{id}"
            x = requests.get(url, headers = header)
            x = x.json()
            print (x)
            attendance = x["Attendance"]
            attendance = attendance[1]

            if attendance == "Present":
                buttonPic = tk.PhotoImage(file="src/images/selected.png")
            else:
                buttonPic = tk.PhotoImage(file="src/images/unselected.png")
            
            button = tk.Button(window, image = buttonPic, bg = "black", activebackground="black", borderwidth=0, command=lambda i=i: markAttendance(username, passW, studentList[i], button, i, id, homeButton, text, text2, time, settingsButton, logoutButton, facialRegisterButton, manualRegisterButton, timetablesButton, modifyClassButton))
            button.image = buttonPic
            button.place(x=1200, y=325 + (i * 100), anchor="center")

            buttonPic = tk.PhotoImage(file="src/images/cross.png")
            button = tk.Button(window, image = buttonPic, bg = "black", activebackground="black", borderwidth=0, command=lambda i=i: unmarkAttendance(username, passW, studentList[i], button, i, id, homeButton, text, text2, time, settingsButton, logoutButton, facialRegisterButton, manualRegisterButton, timetablesButton, modifyClassButton))
            button.image = buttonPic
            button.place(x=1280, y=325 + (i * 100), anchor="center")

        text.configure(text=studentListString, font=("Poppins", 40))
        text.place(x=300, y=285, anchor="nw")

        buttonPic = tk.PhotoImage(file="src/images/homeButton.png")
        homeButton = tk.Button(window, image = buttonPic, bg = "black", activebackground="black", borderwidth=0, command=lambda button = "" : menu(id, username, passW, homeButton, button, text, text2))
        homeButton.image = buttonPic
        homeButton.place(x=800, y=935, anchor="center")

def markAttendance(username, passW, studentIDs, button, i, id, homeButton, text, text2, time, settingsButton, logoutButton, facialRegisterButton, manualRegisterButton, timetablesButton, modifyClassButton):
    homeButton.destroy()
    button.destroy()

    lessonID = selectedLessonID[0]

    url = f"https://api.yungcz.com/teacher/{username}/attendance/mark/{studentIDs}/{lessonID}/Present"
    header = {"password": passW}
    x = requests.get(url, headers = header)
    x = x.json()
    print (x)

    buttonPic = tk.PhotoImage(file="src/images/selected.png")
    selectedButton = tk.Button(image=buttonPic, borderwidth=0, highlightthickness=0, bg="#000000", activebackground="#000000")
    selectedButton.image = buttonPic
    selectedButton.place(x=1200, y=325 + (i * 100), anchor="center")

    buttonPic = tk.PhotoImage(file="src/images/homeButton.png")
    homeButton = tk.Button(window, image = buttonPic, bg = "black", activebackground="black", borderwidth=0, command=lambda: menu(id, username, passW, homeButton, button, text, text2))
    homeButton.image = buttonPic
    homeButton.place(x=800, y=935, anchor="center")

    manualAttendance(id, username, passW, text, text2, time, settingsButton, logoutButton, facialRegisterButton, manualRegisterButton, timetablesButton, modifyClassButton)

def unmarkAttendance(username, passW, studentIDs, button, i, id, homeButton, text, text2, time, settingsButton, logoutButton, facialRegisterButton, manualRegisterButton, timetablesButton, modifyClassButton):
    homeButton.destroy()
    button.destroy()

    lessonID = selectedLessonID[0]

    url = f"https://api.yungcz.com/teacher/{username}/attendance/mark/{studentIDs}/{lessonID}/Absent"
    header = {"password": passW}
    x = requests.get(url, headers = header)
    x = x.json()
    print (x)

    buttonPic = tk.PhotoImage(file="src/images/selected.png")
    selectedButton = tk.Button(image=buttonPic, borderwidth=0, highlightthickness=0, bg="#000000", activebackground="#000000")
    selectedButton.image = buttonPic
    selectedButton.place(x=1200, y=325 + (i * 100), anchor="center")

    buttonPic = tk.PhotoImage(file="src/images/homeButton.png")
    homeButton = tk.Button(window, image = buttonPic, bg = "black", activebackground="black", borderwidth=0, command=lambda: menu(id, username, passW, homeButton, button, text, text2))
    homeButton.image = buttonPic
    homeButton.place(x=800, y=935, anchor="center")

    manualAttendance(id, username, passW, text, text2, time, settingsButton, logoutButton, facialRegisterButton, manualRegisterButton, timetablesButton, modifyClassButton)

def startClient(username, passW, selectedLessonID):
    print("Facial register button pressed")
    facial = camera.facialRecognition(username, passW, selectedLessonID[0])
    facial.run()

def facialRegister(id, username, passW, text, text2, time, settingsButton, logoutButton, facialRegisterButton, manualRegisterButton, timetablesButton, modifyClassButton):

    if len(selectedLessonID) == 0:
        # Show error message using tkinter warning
        text.configure(text="Please select a lesson in timetables\n before continuing", font=("Poppins", 50))
        text.place (x=800, y=550, anchor="center")
        text2.configure(text="GLASS", font=("Poppins", 100))
        text2.place (x=800, y=150, anchor="center")
        time.destroy()
        settingsButton.destroy()
        logoutButton.destroy()
        facialRegisterButton.destroy()
        manualRegisterButton.destroy()
        timetablesButton.destroy()
        modifyClassButton.destroy()

        buttonPic = tk.PhotoImage(file="src/images/homeButton.png")
        homeButton = tk.Button(window, image = buttonPic, bg = "black", activebackground="black", borderwidth=0, command=lambda button = "": menu(id, username, passW, homeButton, button, text, text2))
        homeButton.image = buttonPic
        homeButton.place(x=800, y=900, anchor="center")
    else:

        time.destroy()
        settingsButton.destroy()
        logoutButton.destroy()
        facialRegisterButton.destroy()
        manualRegisterButton.destroy()
        timetablesButton.destroy()
        modifyClassButton.destroy()

        text.configure(text=f"Current Lesson: {selectedLessonID[1]}", font=("Poppins", 25))
        text.place (x=800, y=230, anchor="center")

        text2.configure(text="GLASS", font=("Poppins", 80))
        text2.place (x=800, y=115, anchor="center")

        buttonStartClient = buttonClass("", 570, 570, 20, "black", "Poppins", "src/images/startClientButton.png", lambda: startClient(username, passW, selectedLessonID))
        buttonStartClient.create()

        buttonEditPhoto = buttonClass("", 1250, 570, 20, "black", "Poppins", "src/images/editPhotoButton.png", lambda: editPhoto(username, passW, selectedLessonID, buttonStartClient, buttonEditPhoto, homeButton, text, text2))
        buttonEditPhoto.create()

        buttonPic = tk.PhotoImage(file="src/images/homeButton.png")
        homeButton = tk.Button(window, image = buttonPic, bg = "black", activebackground="black", borderwidth=0, command=lambda button = "": menu(id, username, passW, homeButton, button, text, text2))
        homeButton.image = buttonPic
        homeButton.place(x=800, y=935, anchor="center")

        #import camera
        #print("Facial register button pressed")
        #facial = camera.facialRecognition(username, passW, selectedLessonID)
        #facial.run()


def selectLesson(lessonID, lessonName, teacherIDs, studentIDs, lessonTime, button, i, id, homeButton, username, passW, text, text2, time, settingsButton, logoutButton, facialRegisterButton, manualRegisterButton, timetablesButton, modifyClassButton):
    global selectedLessonID
    print ("STUDENTIDS: " + str(studentIDs))
    selectedLessonID = [lessonID, lessonName, teacherIDs, studentIDs, lessonTime]

    homeButton.destroy()
    button.destroy()

    buttonPic = tk.PhotoImage(file="src/images/selected.png")
    selectedButton = tk.Button(image=buttonPic, borderwidth=0, highlightthickness=0, bg="#000000", activebackground="#000000")
    selectedButton.image = buttonPic
    selectedButton.place(x=1300, y=390 + (i * 100), anchor="center")

    buttonPic = tk.PhotoImage(file="src/images/homeButton.png")
    homeButton = tk.Button(window, image = buttonPic, bg = "black", activebackground="black", borderwidth=0, command=lambda: menu(id, username, passW, homeButton, button, text, text2))
    homeButton.image = buttonPic
    homeButton.place(x=800, y=900, anchor="center")

    timetable(id, username, passW, text, text2, time, settingsButton, logoutButton, facialRegisterButton, manualRegisterButton, timetablesButton, modifyClassButton)

def settings(button):
    print ("Settings button pressed")

def logout(text, text2, time, settingsButton, logoutButton, facialRegisterButton, manualRegisterButton, timetablesButton, modifyClassButton):
    time.destroy()
    settingsButton.destroy()
    logoutButton.destroy()
    facialRegisterButton.destroy()
    manualRegisterButton.destroy()
    timetablesButton.destroy()
    modifyClassButton.destroy()
    text.destroy()
    text2.destroy()
    button = ""
    on_button_click(button)

def timetable(id, username, passW, text, text2, time, settingsButton, logoutButton, facialRegisterButton, manualRegisterButton, timetablesButton, modifyClassButton):

    # Change the background to timetablebg.png
    image = tk.PhotoImage(file="src/images/timetablebg.png")
    background_label.configure(image=image)
    background_label.image = image
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    url = f"https://api.yungcz.com/teacher/{username}/timetables/"
    header = {"password": passW}
    x = requests.get(url, headers = header)

    # Get JSON data
    x = x.json()
    x = x["Lessons"]
    print (x)

    lessonsToday = []

    for i in range(len(x)):
        print (x[i])
        lessonID = x[i][0]
        lessonName = x[i][1]
        teacherIDs = x[i][2]
        studentIDs = x[i][3]
        lessonTime = x[i][4]

        # Convert the lessonTime to a datetime object, no time
        lessonTime = datetime.datetime.strptime(lessonTime, "%Y-%m-%dT%H:%M:%S")
        lessonDate = lessonTime.date()

        # Get todays date
        date = datetime.datetime.now().date()

        if date == lessonDate:
            lessonsToday.append([lessonID, lessonName, teacherIDs, studentIDs, lessonTime])

    print (lessonsToday)

    if lessonsToday == []:
        text.configure(text="No lessons today")
        text.place (x=800, y=550, anchor="center")
        text2.configure(text="GLASS", font=("Poppins", 100))
        text2.place (x=800, y=150, anchor="center")
        time.destroy()
        settingsButton.destroy()
        logoutButton.destroy()
        facialRegisterButton.destroy()
        manualRegisterButton.destroy()
        timetablesButton.destroy()
        modifyClassButton.destroy()

        buttonPic = tk.PhotoImage(file="src/images/homeButton.png")
        homeButton = tk.Button(window, image = buttonPic, bg = "black", activebackground="black", borderwidth=0, command=lambda button = "": menu(id, username, passW, homeButton, button, text, text2))
        homeButton.image = buttonPic
        homeButton.place(x=800, y=900, anchor="center")
    else:
        text.configure(text="")

        text2.configure(text="")


        unselected = tk.PhotoImage(file="src/images/unselected.png")
        selected = tk.PhotoImage(file="src/images/selected.png")

        lessonsnames = ""
        lessonstimes = ""

        for i in range (len(lessonsToday)):
            lessonID = lessonsToday[i][0]
            lessonName = lessonsToday[i][1]
            teacherIDs = lessonsToday[i][2]
            studentIDs = lessonsToday[i][3]
            lessonTime = lessonsToday[i][4]

            # For every lesson, get the lesson time and print them in a line below each other

            lessonTime = lessonTime.strftime("%H:%M")
            lessonsnames = lessonsnames + lessonName + "\n"
            lessonstimes = lessonstimes + lessonTime + "\n"

            try:
            
                if lessonID == selectedLessonID[0]:
                    buttonPic = tk.PhotoImage(file="src/images/selected.png")
                else:
                    buttonPic = tk.PhotoImage(file="src/images/unselected.png")
            except:
                buttonPic = tk.PhotoImage(file="src/images/unselected.png")

            # Each button has a command that calls the selectLesson function, passing the lessonID, button and i of that button
            button = tk.Button(window, image = buttonPic, bg = "black", activebackground="black", borderwidth=0, command=lambda lessonID=lessonsToday[i][0], lessonName=lessonsToday[i][1], teacherIDs=lessonsToday[i][2], studentIDs=lessonsToday[i][3], lessonTime = lessonsToday[i][4], i=i: selectLesson(lessonID, lessonName, teacherIDs, studentIDs, lessonTime, button, i, id, homeButton, username, passW, text, text2, time, settingsButton, logoutButton, facialRegisterButton, manualRegisterButton, timetablesButton, modifyClassButton))
            button.image = buttonPic
            button.place(x=1300, y=390 + (i * 100), anchor="center")

        text = tk.Label(window, text=lessonsnames, bg="black", fg="white", font=("Poppins", 40))
        text.place(x=450, y=250 + (i * 100), anchor="center")

        text2 = tk.Label(window, text=lessonstimes, bg="black", fg="white", font=("Poppins", 40))
        text2.place(x=1100, y=250 + (i * 100), anchor="center")


        buttonPic = tk.PhotoImage(file="src/images/homeButton.png")
        homeButton = tk.Button(window, image = buttonPic, bg = "black", activebackground="black", borderwidth=0, command=lambda: menu(id, username, passW, homeButton, button, text, text2))
        homeButton.image = buttonPic
        homeButton.place(x=800, y=900, anchor="center")
        

        time.destroy()
        settingsButton.destroy()
        logoutButton.destroy()
        facialRegisterButton.destroy()
        manualRegisterButton.destroy()
        timetablesButton.destroy()
        modifyClassButton.destroy()


def menu(id, username, passW, homeButton, button, text, text2):
    try:
        for widgets in window.winfo_children():
            print (widgets)
            if type(widgets) == tk.Button:
                widgets.destroy()
        
        text.destroy()
        text2.destroy()
        button.destroy()

    except Exception as e:
        print (e)
        
    # Change the background to black
    image = tk.PhotoImage(file="src/images/black.png")
    background_label.configure(image=image)
    background_label.image = image
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    if datetime.datetime.now().hour < 12:
        timeOfTheDay = "Morning"
        timeSuffix = "AM"
    elif datetime.datetime.now().hour < 18:
        timeOfTheDay = "Afternoon"
        timeSuffix = "PM"
    else:
        timeOfTheDay = "Evening"
        timeSuffix = "PM"

    # Format todays date to day of the week, day, month, time

    # Get the date
    date = datetime.datetime.now()
    # Get the day of the week
    day = date.strftime("%A")
    # Get the day of the month
    dayNum = date.strftime("%d")
    # Get the month
    month = date.strftime("%B")
    # Get the time
    time = date.strftime("%H:%M")

    if dayNum == "01":
        dayNum = "1st"
    elif dayNum == "02":
        dayNum = "2nd"
    elif dayNum == "03":
        dayNum = "3rd"
    elif dayNum == "21":
        dayNum = "21st"
    elif dayNum == "22":
        dayNum = "22nd"
    elif dayNum == "23":
        dayNum = "23rd"
    elif dayNum == "31":
        dayNum = "31st"
    else:
        dayNum = dayNum + "th"

    print ("ID in menu: ",id)
    
    print (username)
    url = f"https://api.yungcz.com/id-to-name/{username}/{id}"

    header = {"password": passW}
    x = requests.get(url, headers = header)
    # Get JSON data
    x = x.json()
    print ("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",x)
    # Get the name
    firstname = x["firstname"]
    lastname = x["lastname"]

    # Text on (130, 80)
    text = tk.Label(window, text=f"Good {timeOfTheDay}", bg="black", fg="white", font=("Poppins", 30))
    text.place(x=130, y=75)

    # Text on (130, 80)
    text2 = tk.Label(window, text=f"{firstname}", bg="black", fg="white", font=("Poppins Medium", 65))
    text2.place(x=130, y=125)

    time = tk.Label(window, text=f"{day} {dayNum} {month} {time} {timeSuffix}", bg="black", fg="white", font=("Poppins", 30))
    time.place(x=810, y=75)

    settingsPic = tk.PhotoImage(file="src/images/settings.png")
    logoutPic = tk.PhotoImage(file="src/images/logout.png")
    facialRegisterPic = tk.PhotoImage(file="src/images/facialRegisterButton.png")
    manualRegisterPic = tk.PhotoImage(file="src/images/manualRegisterButton.png")
    timetablesPic = tk.PhotoImage(file="src/images/timetablesButton.png")
    modifyClassPic = tk.PhotoImage(file="src/images/modifyClassButton.png")

    settingsButton = tk.Button(window, image=settingsPic, bg="black", activebackground="black", borderwidth=0, command= lambda: settings(settingsButton))
    settingsButton.image = settingsPic
    settingsButton.place(x=1205, y=155)

    logoutButton = tk.Button(window, image=logoutPic, bg="black", activebackground="black", borderwidth=0, command= lambda: logout(text, text2, time, settingsButton, logoutButton, facialRegisterButton, manualRegisterButton, timetablesButton, modifyClassButton))
    logoutButton.image = logoutPic
    logoutButton.place(x=1325, y=155)

    facialRegisterButton = tk.Button(window, image=facialRegisterPic, bg="black", activebackground="black", borderwidth=0, command= lambda: facialRegister(id, username, passW, text, text2, time, settingsButton, logoutButton, facialRegisterButton, manualRegisterButton, timetablesButton, modifyClassButton))
    facialRegisterButton.image = facialRegisterPic
    facialRegisterButton.place(x=115, y=290)

    manualRegisterButton = tk.Button(window, image=manualRegisterPic, bg="black", activebackground="black", borderwidth=0, command= lambda: manualAttendance(id, username, passW, text, text2, time, settingsButton, logoutButton, facialRegisterButton, manualRegisterButton, timetablesButton, modifyClassButton))
    manualRegisterButton.image = manualRegisterPic
    manualRegisterButton.place(x=115, y=730)

    timetablesButton = tk.Button(window, image=timetablesPic, bg="black", activebackground="black", borderwidth=0, command= lambda: timetable(id, username, passW, text, text2, time, settingsButton, logoutButton, facialRegisterButton, manualRegisterButton, timetablesButton, modifyClassButton))
    timetablesButton.image = timetablesPic
    timetablesButton.place(x=860, y=290)

    modifyClassButton = tk.Button(window, image=modifyClassPic, bg="black", activebackground="black", borderwidth=0, command= lambda: logout(logoutButton))
    modifyClassButton.image = modifyClassPic
    modifyClassButton.place(x=860, y=590)

def on_button_login(username, password, button):
    url = "https://api.yungcz.com/login/" + username.get()
    header = {"password": password.get()}
    x = requests.get(url, headers = header)
    print(x.text)
    if "Successful" in x.text:
        user = username.get()
        passW = password.get()
        username.destroy()
        password.destroy()
        button.destroy()
        print("Successful")
        x = x.json()
        id = x["Successful"]
        homeButton = ""
        text = ""
        text2 = ""
        menu(id, user, passW, homeButton, button, text, text2)
    else:
        text = tk.Label(window, text="Incorrect username or password", bg="black", fg="red", font=("Poppins", 20))
        text.place(x=800, y=900, anchor="center")

def on_button_click(button):
    print("Button clicked!")

    try:
        button.destroy()
    except:
        pass
    # Change the background to loginbg.png
    image = tk.PhotoImage(file="src/images/loginbg.png")
    background_label.configure(image=image)
    background_label.image = image
    # Move the login button down to (560, 760)
    buttonC = buttonClass("", 797, 808, 20, "black", "Poppins", "src/images/teacherLoginButton.png", lambda: on_button_login(username, password, buttonC))
    buttonC.create()

    username = tk.Entry(window, bg="black", fg="white", font=("Poppins", 30, "underline"), borderwidth=0, justify = "center")
    username.place(x=540, y=450)
    
    # Create an entry box from (560, 610) to (1035, 705) with a background image photo that has a width of 475 and a height of 95, with the text font Poppins and size 30 with the text "Teacher Login"
    password = tk.Entry(window, bg="black", fg="white", font=("Poppins", 30, "underline"), borderwidth=0, justify = "center", show="*")
    password.place(x=540, y=630)


buttonPic = tk.PhotoImage(file="src/images/teacherLoginButton.png")

# Create a button from (560, 610) to (1035, 705) with a background image photo that has a width of 475 and a height of 95, with the text font Poppins and size 30 with the text "Teacher Login"
#button = tk.Button(window, image=buttonPic, bg="black", activebackground="black", borderwidth=0, width=475, height=95, command= lambda: on_button_click(button))
#button.place(x=560, y=610)

buttonC = buttonClass("", 797, 658, 20, "black", "Poppins", "src/images/teacherLoginButton.png", lambda: on_button_click(buttonC))
buttonC.create()

# Run the main loop
window.mainloop()
