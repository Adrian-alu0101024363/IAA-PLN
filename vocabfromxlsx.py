from asyncio.windows_events import NULL
import csv
import spacy
import re
import pandas as pd
import xlrd
from autocorrect import Speller
from spacymoji import Emoji

def check(token, options = (1,1,1,1,1,1,1,1)):
  param = list(options)
  if (token.is_digit and param[7]): return False
  if (token.is_punct and param[0]): return False
  if (token.is_stop and param[1]): return False
  if (token.like_num and param[2]): return False
  if (token.is_space and param[3]): return False
  if (token.like_url and param[4]): return False
  if (token.is_quote and param[5]): return False
  if ((token.is_left_punct or token.is_right_punct) and param[6]): return False
  return True

def generateTokens(case_flag = True):
  list_tokens = []
  ignore = ('@','-','+','.',',','~','','"','\'','/','(',')','$','&',':','?','^','=')
  nlp = spacy.load("en_core_web_sm")
  emoji = Emoji(nlp)
  nlp.add_pipe(emoji, first=True)
  print("Parsing file")
  with open('COV_train.csv', encoding="utf-8") as csv_file:
    csv_reader = pd.read_csv(csv_file, delimiter=',',compression='gzip')
    for row in csv_reader:
      for line in row:
        #checking = spell(line) #correct spelling mistakes
        doc = nlp(line)
        if (doc._.has_emoji): doc._.emoji_desc
        for token in doc:
          if (check(token)):
            if (not token.lemma_.startswith(ignore) and not token.text[0].isdigit()):
              if (case_flag):
                list_tokens.append(token.lemma_.lower())
              else:
                list_tokens.append(token.lemma_)
  return list_tokens

def generateTokensDict(filename = 'COV_train.csv', case_flag = True):
  list_tokens = {}
  ignore = ('@','-','+','.',',','~','','"','\'','/','(',')','$','&',':','?','^','=')
  nlp = spacy.load("en_core_web_sm")
  print("Parsing file")
  with open(filename, encoding="utf-8") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
      for line in row:
        #checking = spell(line) #correct spelling mistakes
        line = bytes(line, 'utf-8').decode('utf-8', 'ignore')
        doc = nlp(line)
        for token in doc:
          if (check(token)):
            if (not token.lemma_.startswith(ignore) and not token.text[0].isdigit()):
              if (case_flag):
                if (token.lemma_.lower() in list_tokens):
                  iter = list_tokens.get(token.lemma_.lower())
                  list_tokens.update({token.lemma_.lower(): iter+1})
                else:
                  list_tokens.update({token.lemma_.lower(): 1})
              else:
                if (token.lemma_ in list_tokens):
                  iter = list_tokens.get(token.lemma_)
                  list_tokens.update({token.lemma_: iter+1})
                else:
                  list_tokens.update({token.lemma_: 1})
  return list_tokens

def generateVocab():
  original = pd.read_excel('COV_train.xlsx')
  original.to_csv(header=None, index=False).strip('\n').split('\n')
  tokens = generateTokens()
  print("Removing duplicates")
  finalTokens = list(set(tokens))
  #spell = Speller()
  #final = [spell(token) for token in finalTokens]
  print("Sorting by alphabetical order")
  finalTokens.sort()
  return finalTokens

def printVocab(finalTokens):
  vocabulary = open("vocabulario.txt", "w", encoding="utf8")
  print("Writting vocabulary to file")
  vocabulary.write("Numero de palabras: " + str(len(finalTokens)) + "\n")
  for element in finalTokens:
    vocabulary.write(element + "\n")
  vocabulary.close()

#printVocab(generateVocab())
