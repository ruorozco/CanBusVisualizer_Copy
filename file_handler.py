import json
import subprocess
import sys
import csv
import os
import xml.etree.cElementTree as ET
from PyQt5.QtWidgets import QApplication, QFileDialog
from tkinter import messagebox


class FileHandler:
    """
    Handle saving and retrieving of JSON objects/files
    """

    @staticmethod
    def save_project(project_info):
        """
        Saves project python dictionary into user-defined directory as a .JSON file.

        Parameters:
                project_info (dict()): Project dictionary

        Returns:
                0 if successful, else -1.
        """
        # Get first key/value pair in the dictionary
        project_name = list(project_info.items())[0][1]

        # Loop directory prompt until success or cancel
        while True:
            try:
                # Prompt user for path
                path = FileHandler.prompt_dir()
                # Create project directory and update path with new directory
                path = FileHandler.create_dir(project_name, path)
                # Create config.json file
                FileHandler.create_file(path, ".json", project_info, "CONFIG")
                # Update CURRENT_WORKING_PROJECT.JSON
                FileHandler.update_current_project(path)
                # Creating packet_data.json with preset Json dictionary 
                FileHandler.make_preset_json(path)
                #Creating blacklist for user
                FileHandler.make_blacklist(path)
                #Creating decoded_data.json for user
                FileHandler.make_decoded_data(path)
                #Create Map for user
                FileHandler.make_map(path)
                
                return 0
            # The user has tried to create an already existing directory
            except FileExistsError:
                messagebox.showerror(title="CAN Bus Visualizer", message="Folder Already Exists!")
            except FileNotFoundError:
                break
        return -1



    @staticmethod
    def make_map(path):
        newfile = open(path+"/map.json", "w")
        newfile.close()
    
    @staticmethod
    def make_decoded_data(path):
        newfile = open(path+"/decoded_data_json.json", "w")
        newfile.close()

    @staticmethod
    def make_blacklist(path):
        newfile = open(path+"/blacklist.txt", "w")
        newfile.close()

    @staticmethod
    def update_current_project(path):

        """
        Updates the Current_Working_Project.json with the new provided user path

        Parameters:
                path: the new folder path of the user
        """

        # This code can NOT be substitued with get_curr_project()
        # This code Reads the path of the c.w.p. json file
        with open("Current_Working_Project.json", "r") as jsonFile:
                    data = json.load(jsonFile)
                    data["Project_path"] = path

        # This code dumps the new path to the c.w.p. json file
        with open("Current_Working_Project.json", "w") as jsonFile:
            json.dump(data, jsonFile)
    
    @staticmethod
    def get_current_project():

        with open("Current_Working_Project.json", "r") as jsonFile:
            data = json.load(jsonFile)
            return data["Project_path"]


    @staticmethod
    def make_preset_json(path):
        """
        Makes and writes Json Dictionary for the file packet_data.json in the users directory

        Parameters:
                path: the folder path of the user
        """
        # Create packet_data.json for user folder
        with open(path+"/packet_data.json", "w") as jsonFile:
            json_string = {
                            "packets": [
                                {
                                    "timestamp": "-",
                                    "id": "-",
                                    "s": "-",
                                    "dl": "-",
                                    "channel": "-",
                                    "annotate": "-"
                                }
                            ]
                        }
            json.dump(json_string, jsonFile)

    @staticmethod
    def export_to_csv(py_dict):
        """
        Exports python dictionary into user-defined directory as a .CSV file.

        Parameters:
                py_dict (dict()): Python dictionary data

        Returns:
                0 if successful, else -1.
        """
        # Get file information
        file_info = FileHandler.prompt_file_save()
        # If file saved
        if file_info:
            # Create CSV file
            FileHandler.create_file(file_info[0], file_info[2], py_dict, file_name=file_info[1])
            return 0
        return -1

    @staticmethod
    def export(py_dict):
        """
        Exports python dictionary into user-defined directory as a .XML file.

        Parameters:
                py_dict (dict()): Python dictionary data

        Returns:
                0 if successful, else -1.
        """
        # Get file information
        file_info = FileHandler.prompt_file_save()
        # If file saved
        if file_info:
            # Create XML file
            FileHandler.create_file(file_info[0], file_info[2], py_dict, file_name=file_info[1])
            return 0
        return -1

    @staticmethod
    def create_dicts():
        py_dict = {}
        path = FileHandler.get_current_project()
        j_file = open(path+"/CONFIG.json", 'r')
        # d_file = open(path+"/decoded_data_json.json", 'r')
        # m_file = open(path+"/map.json", 'r')
        # p_file = open(path+"/packet_data.json", 'r')
        data_dict_j = json.loads(j_file.read())
        # data_dict_d = json.loads(d_file.read())
        # data_dict_m = json.loads(m_file.read())
        # data_dict_p = json.loads(p_file.read())
        py_dict["Project_Config"] = data_dict_j
        # py_dict["Decoded"].append(data_dict_d)
        # py_dict["Map"].append(data_dict_m)
        # py_dict["Packet_Data"] = data_dict_p
        return py_dict
    
    @staticmethod
    def create_file(path, file_type, file_contents, file_name="place_holder"):
        """
        File creator

        Parameters:
                path String: path
                file_type String: file extension, Ex. (.json)
                file_contents dict: data to be exported
                file_name String: optional file name
        """
        # Create .json file
        if file_type == ".json":
            FileHandler.create_json_file(path, file_name, file_contents)
        # Create .csv file
        if file_type == ".csv":
            FileHandler.create_csv_file(path, file_name, file_contents)
        # Create .xml file
        if file_type == ".xml":
            FileHandler.create_xml_file(path, file_name, file_contents)

    @staticmethod
    def create_dir(dir_name, path):
        """
        Provide simple API for creating a directory.

        Parameters:
                dir_name str: Name of the directory
                path str: Path of the directory
        """
        path = path + "/" + dir_name
        print("Current Path: "+path)
        os.mkdir(path)
        return path

    @staticmethod
    def create_json_file(path, file_name, py_dict):
        with FileHandler.file_opener(path, file_name, ".json") as json_file:
            json_object = json.dumps(py_dict, indent=2)
            json_file.write(json_object)
            json_file.close()

    @staticmethod
    def create_csv_file(path, file_name, py_dict):
        with FileHandler.file_opener(path, file_name, ".csv") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=FileHandler.create_field_names(py_dict))
            writer.writeheader()
            writer.writerow(py_dict)

    @staticmethod
    def create_xml_file(path, file_name, py_dict, root_name="Project_Configuration"):
        root = ET.Element(root_name)
        for key in list(py_dict.keys()):
            e = ET.SubElement(root, key)
            for key_n in list(py_dict[key].keys()):
                ET.SubElement(e, key_n).text = py_dict[key][key_n]
        tree = ET.ElementTree(root)
        tree.write(path+"/"+file_name+".xml")

    @staticmethod
    def prompt_file_open():
        app = QApplication(sys.argv)
        path = QFileDialog.getOpenFileName()[0]
        return FileHandler.parse_file_info(path)

    @staticmethod
    def prompt_file_save():
        app = QApplication(sys.argv)
        path = QFileDialog.getSaveFileName(filter="CSV files (*.csv);; XML files (*.xml)")
        if path[1] == 'XML files (*.xml)':
            new_path = path[0]+".xml"
        elif path[1] == 'CSV files (*.csv)':
            new_path = path[0]+".csv"
        return FileHandler.parse_file_info(new_path)
    
    @staticmethod
    def prompt_dir():
        app = QApplication(sys.argv)
        return QFileDialog.getExistingDirectory()

    @staticmethod
    def file_opener(path, file_name, file_type, flag="w"):
        return open(path + "/" + file_name + file_type, flag)

    @staticmethod
    def parse_file_info(path):
        if not path:
            return []
        file_name_split = FileHandler.get_path_last(path, "/").split(".")
        path = FileHandler.remove_path_last(path, 1)
        file_name = file_name_split[0]
        file_type = "." + file_name_split[1]
        return [path, file_name, file_type]

    @staticmethod
    def get_path_last(path, delimiter="/"):
        return path.split(delimiter)[-1]

    @staticmethod
    def remove_path_last(path, remove_count):
        return "/".join(path.split("/")[:-remove_count])

    @staticmethod
    def create_field_names(py_dict):
        key_list = []
        for key in py_dict:
            key_list.append(key)
        return key_list
