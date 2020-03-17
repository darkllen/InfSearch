from parse import helpParse
import collections

def createInvertIndex(FILEPATH, files, startBook):
    invertIndex = {}
    for i in range(len(files)):
        allText = helpParse.getAllTextFromFb2(FILEPATH + files[i])
        splitedText = helpParse.splitByTags(allText)
        words = helpParse.getWordsListWithIndex(splitedText, i, startBook)
        helpParse.addLists(invertIndex, words)
    invertIndex = collections.OrderedDict(sorted(invertIndex.items()))
    return invertIndex

def createMatrixFromIndex(index, num):
    matrix = {k: helpParse.transformIndexToMatrix(v, num) for k, v in index.items()}
    matrix = collections.OrderedDict(sorted(matrix.items()))
    return matrix

