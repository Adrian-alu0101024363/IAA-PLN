import pandas as pd
import os
import json
import math
import spacy
import re
from symspellpy import SymSpell, Verbosity
import pkg_resources
from vocabfromxlsx import check

sym_spell = SymSpell()
dictionary_path = pkg_resources.resource_filename(
    "symspellpy", "frequency_dictionary_en_82_765.txt"
)
sym_spell.load_dictionary(dictionary_path, 0, 1)


def calculateProbOfLine(tokens):
  r1 , r2 = languageDicts()
  probabilityN = 0
  originalN = pd.read_excel('Negative.xlsx')
  originalP = pd.read_excel('Positive.xlsx')
  original = pd.read_excel('COV_train.xlsx')
  numberOfTweetsN = len(originalN)
  numberOfTweetsP = len(originalP)
  for token in tokens:
    if token in r1:
      #print(r1[token])
      probabilityN += r1[token]
    else:
      probabilityN += r1['unknow']
  probabilityN += math.log(numberOfTweetsN /len(original))
  print(f'Final: {probabilityN}')
  probabilityP = 0
  for token in tokens:
    if token in r2:
      #print(r2[token])
      probabilityP += r2[token]
    else:
      probabilityP += r2['unknow']
  probabilityP += math.log(numberOfTweetsP /len(original))
  print(f'Final: {probabilityP}')
  return probabilityN, probabilityP

#para generar diccionario del tweet osea que palabras tiene
def generateTokensOfLine(line, case_flag = True):
  list_tokens = []
  ignore = ('@','-','+','.',',','~','','"','\'','/','(',')','$','&',':','?','^','=')
  nlp = spacy.load("en_core_web_sm")
  print("Parsing line")
  #line = bytes(line, 'utf-8').decode('utf-8', 'ignore')
  if not isinstance(line, str): line = ''
  emoji_pattern = re.compile("["
      u"\U0001F600-\U0001F64F"  # emoticons
      u"\U0001F300-\U0001F5FF"  # symbols & pictographs
      u"\U0001F680-\U0001F6FF"  # transport & map symbols
      u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                        "]+", flags=re.UNICODE)
  line = emoji_pattern.sub(r'', line)
  doc = nlp(line)
  for token in doc:
    suggestions = sym_spell.lookup(token.lemma_, Verbosity.CLOSEST,max_edit_distance=2)
    if (len(suggestions) > 0):
      token.lemma_ = suggestions[0].term
    if (check(token)):
      if (not token.lemma_.startswith(ignore) and not token.text[0].isdigit()):
        if (case_flag):
          list_tokens.append(token.lemma_.lower())
        else:
          list_tokens.append(token.lemma_)
  return list_tokens

def languageDicts():
  with open('positive_corpus.json') as json_file:
    data = json.load(json_file)
  resultDictP = {}
  for key in data:
    resultP = (data.get(key) + 1) / (len(data)+37201)
    probability = math.log(resultP)
    resultDictP.update({key: probability})
  resultDictN = {}
  with open('negative_corpus.json') as json_file:
    dataN = json.load(json_file)
  #numberOfTweets = len(originalN)
  for key in dataN:
    resultN = (dataN.get(key) + 1) / (len(dataN)+37201)
    probabilityN = math.log(resultN)
    resultDictN.update({key: probabilityN})
  return resultDictN, resultDictP

df = pd.read_excel('Positive.xlsx')
lines = df.iloc[:,0]
#print(lines.head(5))
jisho = generateTokensOfLine("bad bad bad bad")
calculateProbOfLine(jisho)
count = 0
countP = 0
for line in lines.head(100):
  tokens =generateTokensOfLine(line)
  print(tokens)
  tempN , tempP = calculateProbOfLine(tokens)
  if (tempN > tempP): 
    count +=1
  else:
    countP +=1

print(f'Negative: {count}')
print(f'Positive: {countP}')