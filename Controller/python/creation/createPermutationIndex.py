import json
import codecs

def createPermutationIndex(DICTIONARYPATH, name):
    permutationIndex = {}

    jsonFile = codecs.open(DICTIONARYPATH + name, 'r', 'utf-8')
    jsonStr = jsonFile.read()
    uniqueWords = json.loads(jsonStr)

    for i in uniqueWords:
        val = []

        for j in range(0,len(i)):
          val.append(i[j::]+"$"+i[:j:])
        val.append("$"+i)
        permutationIndex[i]=val
    return permutationIndex