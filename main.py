from lib2to3.pgen2 import token
from threading import Thread
from flask import Flask, redirect, url_for, render_template, request
from datetime import date
from file_handler import FileHandler
import json
import os
from threading import Thread
from can_read import read_bus
from can_write import write_bus
from rsync import R_sync
import re
from archive import Archive
from mapper import Mapper

app = Flask(__name__)

today = date.today()
today = today.strftime("%m/%d/%Y")

# Path 
path = os.path.dirname(os.path.realpath(__file__))
os.chdir(path)
json_folder_path = path + "/json"

# Project Page / Table information is comming
headings = ("Timestamp", "ID", "S", "DL", "Channel", "Annotate")
data = []


# Classes for threads
writting = write_bus()
read_class = read_bus(writting)


# This is our Main Page / First Page that appears
@app.route("/", methods=["GET", "POST"])
def main_page():
    if request.method == "POST":
        print("We are here")
        if "upload_folder" in request.form and request.form['upload_folder'] == "go":
            return render_template("project_page.html")
    else:
        return render_template("main_page.html")


# Path of where to save
app.config["UPLOAD_FILES"] = "/GitHub/CS4311_CANBusVisualizer_9/static/img/uploads/"


@app.route("/upload_file", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if request.files:
            files = request.files['Upload']  # Access with the tag name 'Upload' that was setup in html
            print(files)
        return redirect(request.url)
    return render_template("upload_file.html")


# Created for 11/2/2022 Demo, just skeleton for sync functionality
app.config["UPLOAD_FILES"] = "/GitHub/CS4311_CANBusVisualizer_9/static/img/uploads/"

@app.route("/archive_project", methods=["GET", "POST"])
def archive_project():
    if request.method == "POST":
        source = request.form['sourcePath']
        myarchive = Archive(source)
        myarchive.archive()
        # Create if statement that checks the Archive was filled.
        #
        #
        return render_template('archive_project.html', Success="Archive Process Passed")
    return render_template('archive_project.html', Success="")


@app.route("/sync_project", methods=["GET", "POST"])
def sync_project():

    value = False
    if request.method == "POST":
        source=request.form['sourcePath']
        destination = request.form['destinationPath']

        print("Source:", source)
        print("Desitnation:", destination)
        
        if source !="" and destination !="": 
            rsync = R_sync(source, destination)
            rsync.sync()
            value = rsync.compare()
        
            if value == False:
                return render_template('sync_project.html', Success="Sync Process Failed")
            else:
                return render_template('sync_project.html', Success="Sync Process Passed")

    return render_template('sync_project.html', Success="")

@app.route("/get_form", methods=["POST", "GET"])
def get_form():
    if FileHandler.save_project(request.form) == 0:
        return "fwafw"
    return '', 400

# Create Project Page I made these comments for mysef so I dont get confused.- Victor Herrera
@app.route('/create_project', methods=["POST", "GET"])
def create_project():

    has_error = ""
    if request.method == "POST":

        # IF any text boxes are empty we let the user know and start again
        for items,key in request.form.items():
            string_key = str(key)
            result = re.search("[A-Za-z0-9]*$",string_key).string
            if not result: # Failure Case:
                has_error = "ERROR: Please Fill Out All Fields!"
                return render_template("Create_Project.html", date=today, error=has_error)


        # Success Case
        # IF the file hanlder successfully saved the page we can finally go into the project
        if FileHandler.save_project(request.form) == 0:
            return redirect(url_for("project_page"))

        # Failure Case:
        else:
            has_error = "Error: Couldnt Save Project"
            return render_template("Create_Project.html", date=today, error=has_error)

    # First instance of the page
    else:
        return render_template("Create_Project.html", date=today, error=has_error)

# Edit Configuration page
# When working on the project this will allow the user to modify the configuration
@app.route("/edit_config")
def edit_project():
    return render_template("edit_config.html", date=today)


"""
----------------- EVERYTHING UNDER HERE ARE SCRIPTS THAT MANIPULATE THE PAGES -------------------------

"""


# Open the Thread to Read on page Open
@app.route("/project_page", methods=["GET", "POST"])
def project_page():
    # Creating thread to open socket for reading..
    print()
    print("Ruinning Thread to recieve BUS")
    read_class.generate_blacklist()
    thread_read = Thread(target=read_class.receiveDBC)
    thread_read.start()

    return render_template("project_page.html", headings=headings, data=data)


# WRITE TO CAN BUS SCRIPT
@app.route('/send')
def send():
    print("----------------------------------")
    print('Sending packet...')
    writting.sendDBC()

    # Read packet from the reading Thread to update Table
    packet = None
    while not packet:
        packet = read_class.packet
    writeToTable(packet)
    
    mymapper=Mapper()
    mymapper.build_map()

    return render_template('project_page.html', headings=headings, data=data)


def writeToTable(packet):
    if packet:
        packet = str(packet)
        tokens = packet.split()
        dl = " ".join(tokens[8:15])
        channel = tokens[-1]
        annotate = '-'
        data.append([tokens[1], tokens[3], tokens[5], dl, channel, annotate])
        # read_class.packet = None


# Should access Json File of packets and edit Json file


# This is the archive for the Project_Page Call this script with ajax from project_page.html when you push the button
@app.route('/archive')
def archive():
    curr_project = FileHandler.get_current_project()
    myarchive = Archive(curr_project)
    myarchive.archive()
    return render_template('project_page.html')


@app.route('/edit')
def edit():
    return render_template('project_page.html')

#
@app.route('/annotate')
def annotate():
    return render_template('project_page.html')


# Should replay the saved packet json file
@app.route('/replay')
def replay():
    return render_template('project_page.html')


# Should save a json file of packets refer to print("My data: ", tokens[1], tokens[3], tokens[5], myvar) line of code
@app.route('/save')
def save():
    return render_template('project_page.html')


@app.route('/export')
def export():
    FileHandler.export(FileHandler.create_dicts())
    return render_template('project_page.html', headings=headings, data=data)


@app.route('/project_sync', methods=['GET','POST'])
def r_sync():

    if request.method == "POST":
        rsync = R_sync()
        from_folderpath = request.form['from_folderpath']
        to_folderpath = request.form['to_folderpath']

        print(from_folderpath, to_folderpath)
        rsync.sync(from_folderpath, to_folderpath)

    return render_template('sync_project.html')



if __name__ == "__main__":
    # Allows updates on page without running program over again.
    app.run(debug=True)
