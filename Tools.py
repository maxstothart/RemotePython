import os

def remChar(input, toRemove):
    return "".join(char for char in input if char not in toRemove)

def dig2(digit):
    if digit < 10 and digit >= 0:
        return f"0{digit}"
    return f"{digit}"

def getSimilarity(searchString, array, maxLength=5, margin=2):
    Similarity = []
    for i in range(0,len(array)):
        Similarity+=[0]
    #print(len(Similarity))
    sMargin = 0
    for i in range(0,maxLength):
        if i > 0 and sMargin < margin:
            sMargin += 1
        for j in range(0,len(array)):
            if len(array[j].split(".")[0]) > len(searchString)+i:
                Similarity[j] -= 1
                #print(array[j].split(".")[0], j)
            if len(array[j]) > i and len(searchString) > i and searchString[i] in array[j][i-sMargin:i+margin]:
                Similarity[j] += 1
            if i > len(array[j]):
                Similarity[j] -= 1

    return Similarity

def getMostSimilar(searchString, array, maxLength=5, margin=2) -> str:
    if len(array) == 0:
        return ""
    max = (0,0)
    
    if maxLength > len(searchString):
        maxLength = len(searchString)
        #print(maxLength)

    s = getSimilarity(searchString, array, maxLength, margin)

    for i in range(0,len(s)):
        if s[i] > max[1]:
            max = (i,s[i])
    if max[1] >= maxLength-margin:
        #print(s)
        return array[max[0]]
    else:
        print(s)
        return ""

def getDir(dir, fileType=None):
    output = []
    files = os.listdir(dir)
    if fileType == None:
        return files
    for file in files:
        if file[-len(fileType):] == fileType:
            output += [file]
    return output

def GetFoldersToSync(dir1, dir2, fileType=None):
    files1 = getDir(dir1, fileType)
    files2 = getDir(dir2, fileType)
    toSync = [] #[From, To]

    for file in files1:
        if file not in files2:
            toSync += [os.path.join(dir1,file), os.path.join(dir2,file)], 
    for file in files2:
        if file not in files1:
            toSync += [os.path.join(dir2,file), os.path.join(dir1,file)], 
    return [toSync, len(toSync)]
