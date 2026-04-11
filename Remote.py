import os
from .Collect import *
from Tools import *

class remote:
    def __init__(self, hostname, filename, dest="/var/tmp/tmp.py"):
          self.hostname = hostname
          self.filename = filename
          self.dest = dest
          self.pushed = False
          self.AvailableFunctions = []
    def pushFile(self):
         self.Pushed = True
         self.AvailableFunctions = Collect(self.filename, "tmp.py")
         os.system(f"echo rm {self.dest}' | ssh {self.hostname}")
         os.system(f"echo put tmp.py {self.dest} | sftp {self.hostname}")
    def runSafe(self, runDir, funcName, *args):
        x = getFuncFromCollect(self.AvailableFunctions[1])
        Func = getMostSimilar(funcName, x[0])
        FuncString = f"{Func}"
        if args[0] == [""]:
            args = []
        FuncNewVars = args

        if len(args) < len(x[1][x[0].index(Func)]):
            diff = len(x[1][x[0].index(Func)]) - len(args) 
            for var in x[1][x[0].index(Func)][len(args):]:
                if "=" in var:
                    FuncNewVars += var.split("=")[1],
                else:
                    print("ERROR")
                    breakpoint()
                    return False
        if len(FuncNewVars) > 0:
            FuncString += f" {" ".join(FuncNewVars)}"
        self.run(runDir, FuncString)
    def run(self, runDir, *args):
        if not args or args[0] == False:
            return
        if not self.Pushed: self.pushFile()
        
        argString = "".join([f"{arg} " for arg in args])
        print(f"python3 {self.dest} {argString}")
        #check to see if arg count is equal and add defaults if needed
        os.system(f"echo python3 {self.dest} {runDir} {argString} | ssh {self.hostname}")
    
    def delete(self, mode=""):
        self.Pushed = False
        if mode in ["local", ""]:
            try: os.remove("tmp.py")
            except: print("Not Found tmp.py")
            try: os.remove("requirements.txt")
            except: print("Not Found requirements.txt")
        if mode in ["remote", ""]:
             os.system(f"echo rm {self.dest} | ssh {self.hostname}")
    
    def UI(self, RDir):
        if not self.Pushed:
            self.pushFile()
        if len(self.AvailableFunctions) == 0:
            print("No Commands Available")
            return 0
        for i in range(0, len(self.AvailableFunctions[1])):
            print(f"   {self.AvailableFunctions[1][i]}")
        
        CommandIN = input("Enter Command: ")

        if CommandIN != "":
            CommandIN = CommandIN[:-1].replace(", ",",").split("(")
            self.runSafe(RDir, CommandIN[0], CommandIN[1].split(","))