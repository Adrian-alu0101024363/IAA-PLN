from asyncio.windows_events import NULL
import csv
import spacy
import re
import pandas as pd
import xlrd
import pkg_resources
from symspellpy import SymSpell, Verbosity
from spacymoji import Emoji
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

sym_spell = SymSpell()
dictionary_path = pkg_resources.resource_filename(
    "symspellpy", "frequency_dictionary_en_82_765.txt"
)
sym_spell.load_dictionary(dictionary_path, 0, 1)
lemmatizer = WordNetLemmatizer()
en_stops = set(stopwords.words('english'))
punctuations = '''!()-[]{};:'"+-\,<>./?@#|―=$%^&*_~'''
#nltk.download('omw-1.4')


def deEmojify(text):
  regrex_pattern = re.compile(pattern = "["
      u"\U0001F600-\U0001F64F"  # emoticons
      u"\U0001F300-\U0001F5FF"  # symbols & pictographs
      u"\U0001F680-\U0001F6FF"  # transport & map symbols
      u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                          "]+", flags = re.UNICODE)
  return regrex_pattern.sub(r'',text)

def deletehtml(element):
  nohtml = re.sub('<[^<]+?>', '', element)
  if len(nohtml) != len(element) :
    return nohtml
  else:
    return element

def parse(line):
  parsed = ""
  # Borrar emojis
  aux = deEmojify(line)
  # Borrar html tags
  aux2 = deletehtml(aux)
  parsed = parsed + aux2
  # Borrar urls
  finalElement = re.sub(r'https?:\/\/.*[\r\n]*', '', parsed, flags=re.MULTILINE)
  # Borrar numeros
  final = re.sub(r'\d+', '', finalElement)
  return final

def generateTokensDict(filename = 'COV_train.xlsx'):
  list_tokens = {}
  print("Generating Tokens Dictionary")
  original = pd.read_excel(filename)
  lines = original.iloc[:,0]
  list_tokens = []   
  for line in lines:
    parsed = parse(line)
    nltk_token = nltk.word_tokenize(parsed)
    finalElement = ''
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
          if (final in list_tokens):
            iter = list_tokens.get(final)
            list_tokens.update({final: iter + 1})
          else:
            list_tokens.update({final: 1})
          list_tokens.append(final)
  return list_tokens

def generateTokens():
  print("Parsing file")
  original = pd.read_excel('COV_train.xlsx')
  lines = original.iloc[:,0]
  list_tokens = []   
  for line in lines:
    parsed = parse(line)
    nltk_token = nltk.word_tokenize(parsed)
    finalElement = ''
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

def generateVocab():
  tokens = generateTokens()
  print("Removing duplicates")
  finalTokens = list(set(tokens))
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
