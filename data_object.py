class DataObject:

    def __init__(self, dictionary, file_name=None):
        self.data = dictionary
        self.type = DataObject.find_type(dictionary)
        if file_name is None:
            self.file_name = self.find_name(dictionary)
        else:
            self.file_name = file_name

    def get(self, key):
        return self.data[self.type][key]

    def find_name(self, dictionary):
        n_dict = dictionary[self.get_type()]

        for key in n_dict:
            return n_dict[key]

    def get_type(self):
        return self.type

    def get_file_name(self):
        return self.file_name

    def get_data(self):
        return self.data

    @staticmethod
    def find_type(dictionary):
        return list(dictionary.keys())[0]
