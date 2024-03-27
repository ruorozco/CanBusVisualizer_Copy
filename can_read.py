import can
import cantools
import os
import json
from can_write import write_bus
import ast
import time


class read_bus():

    def __init__(self, writer_object):

        self.packet = None
        self.cwd = os.getcwd()
        self.db = cantools.db.load_file(self.cwd + "/dbc_files/comfort.dbc") 
        self.bus = can.interface.Bus(bustype='socketcan', channel='vcan0', bitrate = 250000)
        #self.db_msg = self.db.get_message_by_name("ExampleMessage") # Gets message from DBC file
        self.json_data = {"packets" : []}
        self.decoded_json_data = []

        # Getting correcst DBC information form writer
        self.mywrite = writer_object
        self.dbc_dictionary = self.mywrite.dbc_dictionary
        self.packet_name = self.mywrite.packet_name  
        self.info = self.mywrite.info
        self.msg_data = self.mywrite.msg_data
        self.blacklist = []


    def generate_blacklist(self):

        path = self.get_project_path()
        
        blacklist = []
        with open(path+"/blacklist.txt", "r") as file:
            while (line := file.readline().rstrip()):
                blacklist.append(line)
        print()
        print("Blacklist Contents:", blacklist)
        self.blacklist = blacklist



    def receiveDBC(self):

        while True:
            message = self.bus.recv(4)
            print("Reading:", self.bus.channel_info, " ...")
            self.info = self.mywrite.get_info()
            self.packet_name = self.mywrite.get_packet_name()
            self.msg_data = self.mywrite.get_msg_data()

            
            if message and self.info:
                
                self.decoded = self.db.decode_message(self.info[1][0],  self.msg_data)
                print("----------------------------------")
                print("Reading Packet...")
                print("Decoded Success:", self.db.decode_message(message.arbitration_id, message.data))
                print("----------------------------------")
                print()
                self.packet =  message

                if self.packet:                
                    self.writeJson()
                    self.writeDecodedJson()


    #The code below handles writing to JSON --> Decoded information and raw information

    def writeDecodedJson(self, filename = "decoded_data_json.json"):

        with open("Current_Working_Project.json", "r") as jsonFile:
                    data = json.load(jsonFile)
                    project_path = data["Project_path"]

        filename = project_path + "/"+ filename
        with open(filename, "w", encoding = 'utf8') as f:
            self.packet = str(self.packet)
            tokens = self.packet.split()

        with open(filename, "w", encoding = 'utf8') as f:
            self.decoded = str(self.decoded)
            tokens = self.decoded.split()
            self.decoded_json_data.append(ast.literal_eval(self.decoded))
            json.dump(self.decoded_json_data, f, indent=4)
            print("Decoded Json Created...")
            print()

    def writeJson(self, filename = "packet_data.json"):

        with open("Current_Working_Project.json", "r") as jsonFile:
                    data = json.load(jsonFile)
                    project_path = data["Project_path"]

        filename = project_path + "/"+ filename
        with open(filename, "w", encoding = 'utf8') as f:
            self.packet = str(self.packet)
            tokens = self.packet.split()

            timestamp = time.time() - float(tokens[1])
            channel = tokens[-1]
            annotate = '-'
            self.json_data["packets"].append({
                    "timestamp": timestamp,
                     "id": tokens[3],
                     "s": tokens[5],
                     "dl": tokens[8],
                     "channel": channel,
                      "annotate": annotate
              })
            json.dump(self.json_data, f, indent=4)
            print()
            print("JSON Created...")

    def get_project_path(self):
        with open("Current_Working_Project.json", "r") as jsonFile:
                    data = json.load(jsonFile)
                    return data["Project_path"]

