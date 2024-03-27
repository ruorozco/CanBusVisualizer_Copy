import subprocess

class Archive:
    def __init__(self, folder_path):

        self.from_folderpath = str(folder_path)
        self.to_folderpath = "../CS4311_CANBusVisualizer_9/Archives"

    def archive(self):
        # Running the shell command:
        subprocess.run(f"(mv {self.from_folderpath} {self.to_folderpath})", shell=True)




