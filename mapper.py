import json


class Mapper():
    def __init__(self):
        self.map = []
        self.key = 0
        self.project_path = self.get_project_path()
        self.node_names = []
    
    # Inserts new data into map.json
    def build_map(self):
        
        self.node_names.extend(self.grab_nodes())

        # Can only pass if, if not None
        print(self.node_names)
        if self.node_names:
            for node_name in self.node_names: 
                data =  {"key":self.key , "parent": 0, "name": node_name}
                self.key+=1
                self.map.append(data)
                self.insert_node()

    # Grabs name of the node
    def grab_nodes(self):

        with open(self.project_path + "/decoded_data_json.json") as f:
            node = json.load(f)

        with open(self.project_path + "/map.json") as f:
            json_loaded_nodes = json.load(f)

        loaded_nodes = []

        for packet in json_loaded_nodes :
            name = list(packet.values())[-1]
            loaded_nodes.append(name)

        non_graphed_nodes = []

        for i in range(len(node)):
            node_name = list(node[i].keys())[0]
            if node_name not in loaded_nodes:
                non_graphed_nodes.append(node_name)
                print(node_name)

        return non_graphed_nodes

    def insert_node(self):
        with open(self.project_path + "/map.json", "w") as jsonFile:
                json.dump(self.map, jsonFile)

    def get_project_path(self):
        with open("Current_Working_Project.json", "r") as jsonFile:
                    data = json.load(jsonFile)
                    return data["Project_path"]
