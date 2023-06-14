import nltk 
import re 
import os
import gdown
import sys

def download_punkt():
  nltk.download('punkt')


def read_file(path):
  file = open(path, 'r')

  # Read file
  content = file.read()

  # Close file
  file.close()

  return content

def write_file(path, data):
  file = open(path, 'w')

  # Write file
  file.write(data)

  # Close file
  file.close()

def download_data():
  source = {
    'MweList': read_file(os.path.join('Mwe List','Data','Source.txt'))
  }


  # Download MweList
  gdown.download_folder(source['MweList'], output=os.path.join('Mwe List','Data'))


def tokenizer(data, mwe=[], lang='english'):
  tokens = []
  tokenizer = nltk.MWETokenizer(mwe)
  data = clean_data(nltk.sent_tokenize(data))
  [tokens.append(tokenizer.tokenize(sentence.split())) for sentence in data] 
  return tokens

def clean_data(data):
  result = []

  for i in data:    
    result.append(re.sub(r"[,.]", " , ", i.lower())) 

  return result

if __name__ == '__main__':
  globals()[sys.argv[1]]()