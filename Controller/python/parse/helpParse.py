from lxml import etree
import re
import collections

def transformIndexToMatrix(ind, num):
  res = ""
  count = 0
  i = 0
  for i in range(num):
    if count>=len(ind):
      while len(res) != num:
        res += "0"
      break
    if i==ind[count]:
      count+=1
      res+="1"
    else:
      res+="0"
  return res


def getAllTextFromFb2(path):
  node = etree.parse(path)
  return str(etree.tostring(node.getroot().getchildren()[1], encoding='utf8', method='xml'),'utf-8')

def splitByTags(string):
  pattern = re.compile(r'<[^>]+>')
  return re.split(pattern, string)

def getWordsList(text):
    list = []
    for line in text:
        words = re.findall("[a-zA-Zа-яА-Я]+[^ ]*[a-zA-Zа-яА-Я]+|[a-zA-Zа-яА-Я]+", line)
        words = map(lambda x: x.lower(), words)
        list += words
    list.sort()
    return list

def getWordsListWithIndex(text, num, startBook):
    list = {}
    for line in text:
        words = re.findall("[a-zA-Zа-яА-Я]+[^ ]*[a-zA-Zа-яА-Я]+|[a-zA-Zа-яА-Я]+", line)
        words = map(lambda x: x.lower(), words)
        for w in words:
            if w not in list:
                list[w] = [num+startBook]
    return list

def get2WordsListWithIndex(text, num):
    res = {}
    line = " ".join(text)

    words = re.findall("[a-zA-Zа-яА-Я]+[^ ]*[a-zA-Zа-яА-Я]+|[a-zA-Zа-яА-Я]+", line)
    words = list(map(lambda x: x.lower(), words))
    for w in range(len(words)-1):
        if words[w]+" "+words[w+1] not in res:
            res[words[w]+" "+words[w+1]] = [num]
    return res

def addLists(b, c):
  for k, v in c.items():
    if k not in b:
      b[k] = v
    else:
      b[k]+=v

def getWordsWithCoords(text, fileNum):
    list = {}
    wordCounter = 1
    for line in text:
        words = re.findall("[a-zA-Zа-яА-Я]+[^ ]*[a-zA-Zа-яА-Я]+|[a-zA-Zа-яА-Я]+", line)
        words = map(lambda x: x.lower(), words)
        for w in words:
            if w in list:
              list[w][fileNum].append(wordCounter)
            else:
              list[w] = {fileNum:[wordCounter]}
            wordCounter+=1
    return list

def mergeDicts(dicts, uniqueWords):
  dicts = [collections.OrderedDict(sorted(i.items())) for i in dicts]
  merged = {}
  for i in uniqueWords:
    for j in dicts:
      if i in j:
        if i in merged:
          merged[i].update(j[i])
        else:
          merged[i] = j[i]

  return merged

def get2WordsList(text):
    list = []
    finalList = []
    for line in text:
        words = re.findall("[a-zA-Zа-яА-Я]+[^ ]*[a-zA-Zа-яА-Я]+|[a-zA-Zа-яА-Я]+", line)
        words = map(lambda x: x.lower(), words)
        list += words
    for i in range(len(list)-1):
        finalList.append(list[i]+ " " +list[i+1])
    finalList.sort()
    return finalList

def getListUnique(list):
  unique = []
  for i in range(len(list)-1):
    if list[i] != list[i+1]:
      unique.append(list[i])
  return unique
