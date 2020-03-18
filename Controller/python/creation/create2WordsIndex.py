from parse import helpParse
import collections

def create2wordsIndex(FILEPATH, files):
    words2Index = {}
    for i in range(len(files)):
        allText = helpParse.getAllTextFromFb2(FILEPATH + files[i])
        splitedText = helpParse.splitByTags(allText)
        words = helpParse.get2WordsListWithIndex(splitedText, i)
        helpParse.addLists(words2Index, words)
    words2Index = collections.OrderedDict(sorted(words2Index.items()))
    return words2Index

def create2wordsIndexAuthors(FILEPATH, files):
    words2Index = {}
    for i in range(len(files)):
        allText = helpParse.getAuthor(FILEPATH + files[i])
        splitedText = helpParse.splitByTags(allText)
        words = helpParse.get2WordsListWithIndex(splitedText, i)
        helpParse.addLists(words2Index, words)
    words2Index = collections.OrderedDict(sorted(words2Index.items()))
    return words2Index
def create2wordsIndexTitles(FILEPATH, files):
    words2Index = {}
    for i in range(len(files)):
        allText = helpParse.getBookTitle(FILEPATH + files[i])
        splitedText = helpParse.splitByTags(allText)
        words = helpParse.get2WordsListWithIndex(splitedText, i)
        helpParse.addLists(words2Index, words)
    words2Index = collections.OrderedDict(sorted(words2Index.items()))
    return words2Index
def create2wordsIndexAnnotations(FILEPATH, files):
    words2Index = {}
    for i in range(len(files)):
        allText = helpParse.getBookAnnotation(FILEPATH + files[i])
        splitedText = helpParse.splitByTags(allText)
        words = helpParse.get2WordsListWithIndex(splitedText, i)
        helpParse.addLists(words2Index, words)
    words2Index = collections.OrderedDict(sorted(words2Index.items()))
    return words2Index