
import subprocess
import filecmp

class R_sync:
    def __init__(self, from_folderpath, to_folderpath):

        self.from_folderpath = str(from_folderpath)
        self.to_folderpath = str(to_folderpath)

    def sync(self):

        # Running the shell command:
        subprocess.run(f"(rsync {self.from_folderpath+'/*'} {self.to_folderpath})", shell=True)
        
    def compare(self):

        # Comparing to make sure both directories are identical

        if self.from_folderpath !="" and self.to_folderpath !="": 
            comparison = filecmp.dircmp(self.from_folderpath, self.to_folderpath)
            
            for item in comparison.left_list:
                if item not in comparison.right_list:
                    return False
            return True





