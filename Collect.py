import os, sys, pathlib
def getReferences(mainFile):
    out = []
    ext = []
    internal = []
    dir = [f.name for f in pathlib.Path(os.path.curdir).glob('*') if f.is_file()]
    dir += [str(f) for f in pathlib.Path(os.path.curdir).glob('*/*') if f.is_file()]
    #Get MainFile Libraries
    for line in open(mainFile, 'r'):
        line2 = line.replace("\n", "").replace(",", "").split(" ")

        if line2[0] == "import":
            for lib in line2[1:]:
                out += lib,
        if line2[0] == "from":
            for lib in line2[3:]:
                out += f"{line2[1]}.{lib}",
    
    #If Mainfile Libraries are local, get their libraries
    """
    for lib in out:
        if "." in lib and f"{lib.split(".")[0]}.py" in dir:
            for newLib in getReferences(open(f"{lib.split(".")[0]}.py", 'r')):
                if not newLib in out:
                    out += newLib, 
        elif f"{lib}.py" in dir:
            for newLib in getReferences(open(f"{lib.split(".")[0]}.py", 'r')):
                if not newLib in out:
                    out += newLib, 
    """
    for lib in out:
        if "." in lib:
            if f"{lib.split(".")[0]}.py" in dir:
                if not lib in internal:
                    internal += lib,
                    for newLib in getReferences(f"{lib.split(".")[0]}.py")[1]:
                            if not newLib in ext:
                                ext += newLib,
            elif f"{"\\".join(lib.split(".")[0:2])}.py" in dir:
                if not f"{"\\".join(lib.split(".")[0:2])}.*" in internal:
                    internal += f"{"\\".join(lib.split(".")[0:2])}.*",
                    for newLib in getReferences(f"{"\\".join(lib.split(".")[0:2])}.py")[0]:
                        if newLib not in internal:
                            internal += newLib,
                    for newLib in getReferences(f"{"\\".join(lib.split(".")[0:2])}.py")[1]:
                        if newLib not in ext:
                            ext += newLib,
            else:
                if not f"{"\\".join(lib.split(".")[0:2])}.*" in ext:
                    ext += lib,
        elif f"{lib}.py" in dir:
            if not lib in internal: 
                internal += lib,
                for newLib in getReferences(f"{lib}.py")[1]:
                        if not newLib in ext:
                            ext += newLib,
        else: 
            if lib not in ext: ext += lib,
    return [internal, ext]
def generateReferenceHeader(references):
    dir = os.listdir()
    header = ""
    external = ""
    for entry in references:
        if "." in entry:
            entry = entry.split(".")
            header += f"from {entry[0]} import {entry[1]}\n"
        else:
            header += f"import {entry}\n"
    return header
def getBlock(file, start = [], negStart=[]): 
    for i in range(0,len(start)):
        if start[i][-1] == '*': start[i] = start[i][0:-2]
    out = []
    indices = []
    flag = ""
    foundBlock = -1
    for line in open(file, 'r'):
        if foundBlock >= 0 and line[0:4] == "    ":
            out[foundBlock] = out[foundBlock]+line
        elif line[0] == "\n":
            pass
        elif  XnYDiff(line, start) and not XnYDiff(line, negStart):
            if flag != "":
                out += [flag+line]
            else:
                out += [line]
            indices += [line[:-2]]
            foundBlock = len(out)-1
        else:
            foundBlock = -1
        if line[0] == '@':
            flag = line
        else: flag = ""
    return out, indices
def XnYDiff(x, y):
    """
    X in Y Different Size
    Checks if x contains any of the strings in y.

    Args:
        x (str): The string to check.
        y (list[str]): The list of strings to check for.

    Returns:
        bool: True if any of the strings in y are found at start of x, False otherwise.
    """
    if len(y) == 0:
        return False
    for ent in y:
        if len(x) >= len(ent) and x[0:len(ent)] == ent:
            return True
    return False
def retrieveFunctionsFromReferences(references):
    out = "\n"
    indicies = []
    for ref in references:
        blocks = getBlock(f"{ref.split(".")[0]}.py", ["def "+ref.split(".")[1]])
        for func in blocks[0]:
            if out[-1] != "\n": out += "\n"
            out += func.strip("\n")
        for ind in blocks[1]:
            indicies += ind[4:],
    return out[1:]+"\n", indicies
def retrieveClassesFromReferences(references):
    out = "\n"
    indicies = []
    for ref in references:
        blocks = getBlock(f"{ref.split(".")[0]}.py", ["class "+ref.split(".")[1]])
        for func in blocks[0]:
            if out[-1] != "\n": out += "\n"
            out += func.strip("\n")
        for ind in blocks[1]:
            indicies += ind[6:],
    return out[1:]+"\n", indicies
def retrieveConstantsFromReferences(references):
    out = ""
    for ref in references:
        for line in open(f"{ref.split(".")[0]}.py", 'r'):
            if not line in ["", " ", "\n"]:
                if XnYDiff(line, ["def ", "class "]):
                    break
                if not XnYDiff(line, ["from ", "import ", "\n"]):
                    out += line
    return out

def getFuncFromCollect(col):
    funcNames = []
    funcVars = []
    for func in col:
        funcNames += func.split("(")[0],
        tempFVars = func[len(funcNames[-1])+1:].split(")")[0].split(", ")
        tempFVars2 = []
        for i in range(0,len(tempFVars)):
            OpenBrackets = 0
            for char in tempFVars[i]:
                if char in ["[", "(", "{"]:
                    OpenBrackets += 1
                elif char in ["]", ")", "}"]:
                    OpenBrackets -= 1
            if OpenBrackets > 0 and i+1 < len(tempFVars):
                OpenBrackets = 0
                for char in tempFVars[i:i+1]:
                    if char in ["[", "(", "{"]:
                        OpenBrackets += 1
                    elif char in ["]", ")", "}"]:
                        OpenBrackets -= 1
                if OpenBrackets == 0:
                    tempFVars2 += tempFVars[i]+tempFVars[i+1],
                else:
                    tempFVars2 += tempFVars[i],
            else:
                tempFVars2 += tempFVars[i],
        funcVars += tempFVars2,

    return [funcNames, funcVars]

def externalRunPayload(classes, functions):
    log = "if __name__ == \"__main__\" and len(sys.argv) > 1:\n    os.chdir(sys.argv[1])\n"
    funcNames, funcVars = getFuncFromCollect(functions)
    for i in range(0,len(funcNames)):
        varString = ""
        #print(funcVars)
        for j in range(3,len(funcVars[i])+3):
            if "=" in funcVars[i][j-3] and str(funcVars[i][j-3].split("=")[1]).isdigit():
                varString += f"int(sys.argv[{j}]), "
            elif "=" in funcVars[i][j-3] and str(funcVars[i][j-3].replace(" ","").split("=")[1]) in ["True", "False"]:
                varString += f"bool(sys.argv[{j}]), "
            else:
                varString += f"sys.argv[{j}], "
        log += f"    if sys.argv[2] == \"{funcNames[i]}\": {funcNames[i]}({varString[:-2]})\n"
    return log
    
def Collect(fileIN="main.py", fileOUT="collected.py"):
    newFile = ""
    
    #refHeader
    ref = getReferences(fileIN)
    newFile += generateReferenceHeader(ref[1])+"\n"
    #Get Constant variables
    #breakpoint()
    newFile += retrieveConstantsFromReferences(ref[0]+["main.*"])+"\n"

    #Make Reference File
    if "\\" in fileOUT:
        open("\\".join(fileOUT.split("\\")[0:-1])+"references.txt", 'w').write("\n".join(ref[1]))
    elif "/" in fileOUT:
        open("/".join(fileOUT.split("/")[0:-1])+"references.txt", 'w').write("\n".join(ref[1]))
    else: open("references.txt", 'w').write("\n".join(ref[1]))

    CollectedClasses = retrieveClassesFromReferences(ref[0]+["main.*"])
    CollectedFunctions = retrieveFunctionsFromReferences(ref[0]+["main.*"])
    newFile += CollectedClasses[0]+"\n"
    newFile += CollectedFunctions[0]+"\n"

    #AddRemoteLogic
    newFile += externalRunPayload(CollectedClasses[1],CollectedFunctions[1])+"\n"

    #If Main Function Collection
    newFile += getBlock(fileIN, ["if __name__ == \"__main__\""])[0][0]

    #WriteFile
    open(fileOUT, 'w').write(newFile)
    return  CollectedFunctions[1]

#print(getBlock("main.py", ["class *"])[1])

if 1 and __name__ == "__main__":
    FIN = "main.py"
    FOUT = "collected.py"

    if len(sys.argv) >= 2:
        FIN = sys.argv[1]
    if len(sys.argv) >= 3:
        FOUT = sys.argv[2]
    print(Collect(FIN,FOUT))
