import pandas as pd
import os
import json
import math
import spacy
import re
from symspellpy import SymSpell, Verbosity
import pkg_resources
import time
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from vocabfromxlsx import parse

sym_spell = SymSpell()
dictionary_path = pkg_resources.resource_filename(
    "symspellpy", "frequency_dictionary_en_82_765.txt"
)
sym_spell.load_dictionary(dictionary_path, 0, 1)
lemmatizer = WordNetLemmatizer()
en_stops = set(stopwords.words('english'))
punctuations = '''!()-[]{};:'"\,<>./?@#|―=$%^&*_~'''
#nltk.download('omw-1.4')

def calculateProbOfLine(tokens, r1, r2, sizeN, sizeP, sizeO):
  probabilityN = 0
  probabilityP = 0
  for token in tokens:
    if token in r1:
      #print(r1[token])
      probabilityN += r1[token]
    else:
      probabilityN += r1['unknow']
    if token in r2:
      #print(r2[token])
      probabilityP += r2[token]
    else:
      probabilityP += r2['unknow']
  probabilityN += math.log(sizeN /sizeO)
  #print(f'Final Negative: {probabilityN}')
  probabilityP += math.log(sizeP /sizeO)
  #print(f'Final Positive: {probabilityP}')
  return probabilityN, probabilityP

def generateTokensOfLine(line):
  if not isinstance(line, str): line = ''
  parsed = parse(line) #si no parseo empora 
  nltk_token = nltk.word_tokenize(parsed)
  finalElement = ''
  list_tokens = []
  for element in nltk_token:
    #Comprobar que no es una stopword
    if element not in en_stops:
      text = element.lower()
      finalElement= re.sub(r'[^\w\s]', '', text)
      No_under = finalElement.replace('_', '')
      final = lemmatizer.lemmatize(No_under, 'v')
      if(len(final) > 1):
        suggestions = sym_spell.lookup(final, Verbosity.CLOSEST,max_edit_distance=2)
        if (len(suggestions) > 0 and suggestions[0].term != 'a'):
          final = suggestions[0].term
        list_tokens.append(final)
  return list_tokens

def languageDicts():
  with open('positive_corpus.json') as json_file:
    data = json.load(json_file)
  resultDictP = {}
  for key in data:
    resultP = (data.get(key) + 1) / (len(data)+34969)
    probability = math.log(resultP)
    resultDictP.update({key: probability})
  resultDictN = {}
  with open('negative_corpus.json') as json_file:
    dataN = json.load(json_file)
  #numberOfTweets = len(originalN)
  for key in dataN:
    resultN = (dataN.get(key) + 1) / (len(dataN)+34969)
    probabilityN = math.log(resultN)
    resultDictN.update({key: probabilityN})
  return resultDictN, resultDictP

df = pd.read_excel('COV_train.xlsx')
#df = pd.read_excel('Negative.xlsx')
#df = pd.read_excel('Positive.xlsx')
lines = df.iloc[:,0]
r1 , r2 = languageDicts()
#print(lines.head(5))
#jisho = generateTokensOfLine("bad bad bad bad")
#calculateProbOfLine(jisho, r1, r2)
count = 0
countP = 0
originalN = pd.read_excel('Negative.xlsx')
originalP = pd.read_excel('Positive.xlsx')
original = pd.read_excel('COV_train.xlsx')
numberOfTweetsN = len(originalN)
numberOfTweetsP = len(originalP)
numberOfTweetsO = len(original)
start = time. time()
for line in lines:
  tokens =generateTokensOfLine(line)
  #print(tokens)
  tempN , tempP = calculateProbOfLine(tokens, r1, r2, numberOfTweetsN, numberOfTweetsP, numberOfTweetsO)
  if (tempN > tempP): 
    count +=1
  else:
    countP +=1

end = time. time()
print(end-start)
negativer = (count - numberOfTweetsN) / numberOfTweetsN
positiver = (countP - numberOfTweetsP) / numberOfTweetsP
print(f'Negative Error: {math.fabs(negativer*100)}')
print(f'Positive Error: {math.fabs(positiver*100)}')