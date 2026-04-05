import os
from RemotePython.Collect import *

class remote:
    def __init__(self, hostname, filename, dest="/var/tmp/tmp.py"):
          self.hostname = hostname
          self.filename = filename
          self.dest = dest
    def pushFile(self):
         self.AllowedFunctions, self.AllowedFunctionVariables = getFuncFromCollect(Collect(self.filename, "tmp.py"))
         os.system(f"echo rm {self.dest}' | ssh {self.hostname}")
         os.system(f"echo put tmp.py {self.dest} | sftp {self.hostname}")

    def run(self, runDir, function, *args):
        argString = "".join([f"{arg} " for arg in args])
        print(f"python3 {self.dest} {function} {argString}")
        #check to see if arg count is equal and add defaults if needed
        os.system(f"echo python3 {self.dest} {runDir} {function} {argString} | ssh {self.hostname}")
    def deleteLocal(self):
        os.remove("tmp.py")
        os.remove("references.txt")
    def deleteRemote(self):
         os.system(f"echo rm {self.dest} | ssh {self.hostname}")
    def delete(self):
         self.deleteLocal()
         self.deleteRemote()