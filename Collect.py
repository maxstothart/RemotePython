import os, sys, pathlib
def getReferences(mainFile):
    dir = [f.name for f in pathlib.Path(os.path.curdir).glob('*') if f.is_file()]
    dir += [f.as_posix() for f in pathlib.Path(os.path.curdir).glob('*/*') if f.is_file()]

    internal = []
    external = []
    for line in open(mainFile, 'r'):
        line = line.strip("\n")
        if XnYDiff(line, ["from "]):
            if line.split(" ")[1] == '.':
                for x in line[14:].split(" ,"): #skip past len("from  import ")=13 + len(.) = 14
                    internal += f"{x}.*",
            elif line.split(" ")[1][0] == '.':
                for x in line[13+len(f"{line.split(" ")[1][1:]}"):].split(" ,"): #skip past len("from  import ")=13 + len(.) = 14
                    internal += f"{line.split(" ")[1][1:]}.*",
            elif f"{line.split(" ")[1]}.py" in dir:
                for x in line[len(f"{line.split(" ")[1]}")+13:].split(" ,"):
                    internal += f"{f"{line.split(" ")[1]}"}.{x}",
            elif f"{line.split(" ")[1]}/{line.split(" ")[3]}.py" in dir:
                for x in line[len(f"{line.split(" ")[1]}")+13:].split(" ,"):
                    internal += f"{line.split(" ")[1]}/{line.split(" ")[3]}.*",
            elif f"{line.split(" ")[1].replace('.', '/')}.py" in dir:
                for x in line[len(f"{line.split(" ")[1]}")+13:].split(" ,"):
                    internal += f"{line.split(" ")[1].replace('.', '/')}.*",
            else:
                for x in line[len(f"{line.split(" ")[1]}")+13:].split(" ,"):
                    external += f"{f"{line.split(" ")[1]}"}.{x}",
        elif XnYDiff(line, ["import "]):
            for x in line[7:].split(", "): #skip len("import ")=7
                external += f"{x}",
    
    for ent in internal:
        resp = getReferences(f"{ent.split(".")[0]}.py")
        for ref in resp[0]:
            if ref not in internal:
                internal += ref,
        for ref in resp[1]:
            if ref not in external:
                external += ref,
    return [internal, external]
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
    references = references
    for i in range(len(references)-1, 0, -1):
        ref = references[i]
        for line in open(f"{ref.split(".")[0]}.py", 'r'):
            if not line in ["", " ", "\n"]:
                if XnYDiff(line, ["def ", "class "]):
                    break
                if not XnYDiff(line, ["from ", "import ", "\n"]):
                    out += line
            if len(out) > 0 and out[-1] != "\n":
                out += "\n"
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
        if tempFVars2[0] != '':
            funcVars += tempFVars2,
        else:
            funcVars += [],

    return [funcNames, funcVars]

def externalRunPayload(classes, functions):
    log = "if __name__ == \"__main__\" and len(sys.argv) > 1:\n    os.chdir(sys.argv[1])\n"
    funcNames, funcVars = getFuncFromCollect(functions)

    #Comment Functions
    log += "    \"\"\"\n"
    for i in range(0, len(funcNames)):
        log += f"        {functions[i]}\n"
    log += "    \"\"\"\n"

    for i in range(0,len(funcNames)):
        varString = ""
        #print(funcVars)
        for j in range(3,len(funcVars[i])+3):
            if "=" in funcVars[i][j-3] and str(funcVars[i][j-3].split("=")[1]).isdigit():
                varString += f"int(sys.argv[{j}]), "
            elif "=" in funcVars[i][j-3] and str(funcVars[i][j-3].replace(" ","").split("=")[1]) in ["True", "False"]:
                varString += f"bool(sys.argv[{j}]), "
            elif funcVars[i][j-3] != "":
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
        open("\\".join(fileOUT.split("\\")[0:-1])+"requirements.txt", 'w').write("\n".join(ref[1]))
    elif "/" in fileOUT:
        open("/".join(fileOUT.split("/")[0:-1])+"requirements.txt", 'w').write("\n".join(ref[1]))
    else: open("requirements.txt", 'w').write("\n".join(ref[1]))

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
    return [CollectedClasses[1],CollectedFunctions[1]]

#print(getBlock("main.py", ["class *"])[1])

#print(getReferences("main.py"))

if 1 and __name__ == "__main__":
    FIN = "main.py"
    FOUT = "collected.py"

    if len(sys.argv) >= 2:
        FIN = sys.argv[1]
    if len(sys.argv) >= 3:
        FOUT = sys.argv[2]
    print(Collect(FIN,FOUT))
