from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk import FreqDist, classify, NaiveBayesClassifier
import nltk
import pandas as pd
import json
import re, string, random
#nltk.download('twitter_samples')

def remove_noise(tweet_tokens, stop_words = ()):

  cleaned_tokens = []

  for token, tag in pos_tag(tweet_tokens):
    token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                    '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
    token = re.sub("(@[A-Za-z0-9_]+)","", token)
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                        "]+", flags = re.UNICODE)
    token = regrex_pattern.sub(r'',token)               
    if tag.startswith("NN"):
        pos = 'n'
    elif tag.startswith('VB'):
        pos = 'v'
    else:
        pos = 'a'

    lemmatizer = WordNetLemmatizer()
    #stemmer = PorterStemmer()
    token = lemmatizer.lemmatize(token, pos)
    #token = stemmer.stem(token)
    if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
      cleaned_tokens.append(token.lower())
  return cleaned_tokens

def get_all_words(cleaned_tokens_list):
  for tokens in cleaned_tokens_list:
    for token in tokens:
      yield token

def get_tweets_for_model(cleaned_tokens_list):
  for tweet_tokens in cleaned_tokens_list:
    yield dict([token, True] for token in tweet_tokens)

def generateTokens(filename):
  list_tokens = [[]]
  stop_words = stopwords.words('english')
  print("Generating Tokens Dictionary")
  original = pd.read_excel(filename,header=None)
  for index, data in original.iterrows():
    line = ''
    if isinstance(data[0], str): line = data[0]
    nltk_token = word_tokenize(line)
    element = remove_noise(nltk_token,stop_words)
    list_tokens.append(element)
  return list_tokens

def train():
  print("Getting positive tweets")
  positive_cleaned_tokens_list = generateTokens('Positive.xlsx')
  print("Getting negative tweets")
  negative_cleaned_tokens_list = generateTokens('Negative.xlsx')
  print("Getting all words")
  all_pos_words = get_all_words(positive_cleaned_tokens_list)
  print("Looking up frequency distribution")
  freq_dist_pos = FreqDist(all_pos_words)
  #print(freq_dist_pos.most_common(10))
  print("Generating models")
  positive_tokens_for_model = get_tweets_for_model(positive_cleaned_tokens_list)
  negative_tokens_for_model = get_tweets_for_model(negative_cleaned_tokens_list)
  print("Creating datasets")
  positive_dataset = [(tweet_dict, "Positive")
                        for tweet_dict in positive_tokens_for_model]

  negative_dataset = [(tweet_dict, "Negative")
                        for tweet_dict in negative_tokens_for_model]

  dataset = positive_dataset + negative_dataset
  random.shuffle(dataset)

  train_data = dataset[:23411]
  test_data = dataset[23411:]
  print("Training model")
  classifier = NaiveBayesClassifier.train(train_data)

  print("Accuracy is:", round(classify.accuracy(classifier, test_data)*100,2))

  #print(classifier.show_most_informative_features(10))

  return classifier

def clasify(filename, classifier):
  print("Classifying file")
  df = pd.read_excel(filename, header=None)
  results = open("resumen_alu0101024363.txt", "w", encoding="utf8")
  for index, data in df.iterrows():
    custom_tokens = remove_noise(word_tokenize(data[0]))
    prediction = classifier.classify(dict([token, True] for token in custom_tokens))
    if (prediction == "Positive"):
      results.write("P" + "\n")
    elif (prediction == "Negative"):
      results.write("N" + "\n")
    else:
      print("Something went wrong :(")
  
if __name__ == "__main__":

    classifier = train()
    #clasify('COV_test_g2_debug.xlsx', classifier)
    clasify('COV_test_g2.xlsx', classifier)
    '''
    custom_tweet = "coronavirus bad"

    custom_tokens = remove_noise(word_tokenize(custom_tweet))

    print(custom_tweet, classifier.classify(dict([token, True] for token in custom_tokens)))
  '''