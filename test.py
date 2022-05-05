import pandas as pd
import os
import json
import math
import spacy
from vocabfromxlsx import check

df = pd.read_excel('COV_train.xlsx')
lines = df.iloc[:,0]
print(lines.head(5))
#para generar diccionario del tweet osea que palabras tiene
def generateTokensOfLine(line, case_flag = True):
  list_tokens = []
  ignore = ('@','-','+','.',',','~','','"','\'','/','(',')','$','&',':','?','^','=')
  nlp = spacy.load("en_core_web_sm")
  print("Parsing line")
  #checking = spell(line) #correct spelling mistakes
  line = bytes(line, 'utf-8').decode('utf-8', 'ignore')
  doc = nlp(line)
  for token in doc:
    if (check(token)):
      if (not token.lemma_.startswith(ignore) and not token.text[0].isdigit()):
        if (case_flag):
          list_tokens.append(token.lemma_.lower())
        else:
          list_tokens.append(token.lemma_)
  return list_tokens
jisho = generateTokensOfLine("about to go abroad fish car car car")
print(jisho)
for line in lines.head(2):
  tokens =generateTokensOfLine(line)
  print(tokens)
  #calculateProbofLine(tokens, "modelo_lenguaje_P.txt")
  #calculateProbofLine(tokens, "modelo_lenguaje_N.txt")

def calculateProbOfLine(tokens, file):
  pass