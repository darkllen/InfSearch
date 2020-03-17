import json
import codecs

def create3GramIndex(DICTIONARYPATH, name):
  index = {}

  jsonFile = codecs.open(DICTIONARYPATH + name, 'r', 'utf-8')
  jsonStr = jsonFile.read()
  uniqueWords = json.loads(jsonStr)

  for word in uniqueWords:
    t = None
    if len(word)!=1:
      t = [word[i:i+3] for i in range(0, len(word)-1)]
      t[-1]+="$"
      t.insert(0, "$"+t[0][0:2])
    else:
      t = ["$"+word[0]+"$"]
    for i in t:
      if i in index:
        index[i].append(word)
      else:
        index[i] = [word]
  return index