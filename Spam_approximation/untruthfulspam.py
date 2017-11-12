'''
	Script to detect untruthful reviews from a corpus of reviews.
	The script assigns a divergence score to a pair of reviews to assess their similarity. The greater the score, the more similar
	reviews are.
	Paper cited - "Text Mining and Probabilistic Language Modeling for Online Review Spam Detection" by Xu, et al.
'''

'''
	Dependencies of the class. The different libraries used - 
	1) JSON
	2) RE (Regular Expressions)
	3) NLTK
	4) MATH
	5) similarity, word_similarity functions from short_sentence_similarity
	
'''
import json
from short_sentence_similarity import word_similarity
from short_sentence_similarity import similarity
from featureclass import FeatureClass
from collections import defaultdict
import re
from nltk.corpus import stopwords
import math
import os
import pandas as pd
import numpy as np
'''
	Values of the Jelinek-Mercer smoothing parameters.
	Values chosen on trial and error.
'''
MU = 0.4
NU = 0.8
'''
	Class for assigning divergence score to a pair of reviews.
'''
class UntruthfulSpam:
	'''
		grand_total is the dictionary containing the values of tf(t,D)/|D| for all the terms in the corpus. tf(t,D) is the term frequency of the term in the entire corpus and |D| is the length(in words) of the corpus.
		json_text is a list of dicts containing the entire corpus. Used in functions later.
	'''
	
	grand_total = {}
	json_text = []
	
	'''
		Constructor to initialise grand_total and json_text
	'''
	
	def __init__(self,jsonfile):
		self.json_text = json.load(jsonfile)
		self.grand_total = self.total_frequencies()
	
	'''
		Function to return json_text should the reviewer require it.
	'''
	
	def json_file(self):
		return self.json_text
	
	'''
		Function to vectorize a text.
		Input: a review (text)
		Output: a list of words in text. Removes punctuation and common words according to NLTK Stopwords.
	'''
	
	def vectorize_text(self,text):
		'''
			Function to remove punctuation from text. Uses regular expressions to remove the same.
		'''
	
		def remove_punctuation(text):
			return re.sub('[,.?";:\-!@#$%^&*()]', '', text)
	
		'''
			Function to remove common words (i.e. Stopwords) from a text. Primarily done to reduce size of corpus and so that the prediction is not skewed due to presence of a lot of common words.
		'''
	
		def remove_common_words(text_vector):
			common_words = set(stopwords.words('english'))
			common_words = common_words
			#print common_words
			return [word for word in text_vector if word not in common_words]
			
		text = text.lower()
		#print text
		text = remove_punctuation(text)
			#print text
		words_list = text.split()
		words_list = remove_common_words(words_list)
			#print words_list
		return words_list
	
	'''
		Function to calculate the tf(t,d)/|d| score of each term in the document d. tf(t,d) is the term frequency of term t in the document d and |d| is the length of the document (in words)
		Input: a word vector
		Output: dictionary containing tf(t,d)/|d| score of each term
	'''
	
	def word_frequencies(self,word_vector):
		num_words = len(word_vector)
		frequencies = defaultdict(float)
		for word in word_vector:
			frequencies[word] += 1.0/num_words
		return dict(frequencies)
	
	'''
		Function to calculate the tf(t,D)/|D| score of each term in the corpus. tf(t,D) is the term frequency of term t in the corpus D and |D| is the length (in words) of the entire corpus.
		Input: none
		Output: returns a dictionary containing tf(t,D)/|D| of each term
	'''
	
	def total_frequencies(self):
		num_docs = len(self.json_text)
		#print num_docs
		frequencies = defaultdict(float)
		for item in self.json_text:
			word_vector = self.vectorize_text(item['content'])
			for word in word_vector:
				frequencies[word] += 1.0
		no_of_words = sum(frequencies.values())
		for key in frequencies:
			frequencies[key] /= no_of_words
		return dict(frequencies)
	
	'''
		Calculates the semantic language model probability P_semantic. 
		P_semantic(t1) = sum(association_probability(t1,t2) * (tf(t2,d)/|d|))/|R|
		|R| has been approximated to be 5000 here. R represents the set of term relationships between all the words in the corpus. 
		The approximation is taken as it is computationally expensive.
		Input: word and the word vector of the text.
		Output: The Semantic Score of the term wrt the document.
	'''
	
	def P_semantic(self,word,review_1):
		#words = word_frequencies(review_1)
		P_semantic = 0
		for words in review_1.keys():
			#print words
			#print word_similarity(words,word)
			P_semantic += (word_similarity(words,word) * review_1[words])
		P_semantic /=2060
		#print P_semantic
		return P_semantic
	
	'''
		Function for the language model of a term "word" wrt a document vector "word_vector1". Calculates the probability of the "generation" of the word wrt the document.
		Formula used: P(t|doc) = (1 - MU) * (((1-NU)word_frequencies(word)) + (NU*P_semantic(word,words))) + (MU*grand_total(word))
		Input: word in question and doc vector
		Output: Probability of term wrt document
	'''
	
	def P(self,word,word_vector1):
		words = self.word_frequencies(word_vector1)
		#alsowords = word_frequencies(word_vector2)
		probability = (1-MU)*(((1-NU)*words.get(word,0.0)) + (NU * self.P_semantic(word,words))) + (MU * self.grand_total.get(word,0.0))
		
		return probability
			
	
	'''
		Function to calculate the divergence between the two reviews in question.
		Score = sum(P(word,review_1) * log(P(word,review_1)/P(word,review_2))
		PS - review_1 here is the longer review
		Input: 2 reviews review_1 and review_2
		Output: The divergence score between the two
	'''
	
	def score(self,review_1,review_2):
		#review_1 = self.json_text[0]['content']
		#review_2 = self.json_text[0]['content']
		review_1 = self.vectorize_text(review_1)
		review_2 = self.vectorize_text(review_2)
		all_words = list(set(review_1).union(set(review_2)))
		score = 0.0
		for word in all_words:
			try:
				if len(review_1) >= len(review_2):
					score += -(self.P(word,review_1) * math.log(self.P(word,review_1)/self.P(word,review_2),2))
				else:
					score += -(self.P(word,review_2) * math.log(self.P(word,review_2)/self.P(word,review_1),2))
			except Exception:
				score += 0
		return score
	
	
'''
	opening the file for calculating divergence.
'''

jsonfile = open('hotelreviewsupdated.json')
untruthful = UntruthfulSpam(jsonfile)
json_text = untruthful.json_file()

'''
	divergence scores between consecutive pairs of documents.
'''
'''
scores = []
for i in xrange(20):
	print i
	scores.append(untruthful.score(json_text[i]['content'], json_text[i+1]['content']))
print scores
'''


'''
	Testing on the yelp dataset
'''
negative_list = os.listdir("negative_polarity")
positive_list = os.listdir("positive_polarity")
def preprocess(files_list,root_dir,polarity):
	labeled_class = []
	reviews = []
	actual_class = []
	for j in files_list:
		labeled_class.append(polarity)
		k = str(open(root_dir + '/' + j).read())
		reviews.append(k)
		actual_class.append(str(j.split('_')[0]))
	data = pd.DataFrame({'labeled_class':labeled_class,'review':reviews,'actual_class':actual_class})
	return data

negative_df = preprocess(negative_list, 'negative_polarity','negative')
positive_df = preprocess(positive_list, 'positive_polarity','positive')

'''
	Labeling the training data. Labelled 1 if they are true reviews and -1 if they are spam.
	For example, if the labeled class was positive and actual class is d(i.e. deceptive) it is a fake review.
'''
target = []
for i in positive_df.index:
	if ((positive_df['labeled_class'][i] == 'positive') & (positive_df['actual_class'][i] == 't')):
		target.append(1)
	elif ((positive_df['labeled_class'][i] == 'positive') & (positive_df['actual_class'][i] == 'd')):
		target.append(-1)
	else:
		print 'Error'
positive_df['target'] = target

'''
	The loop below is testing the untruthfulspam class on the examples that are definitely spam. Similar loop can be applied to the negative one 
	as well or to the whole data.
'''
iterations = 0
file1 = open("testfile.txt","w")
g = list()
for index, row in positive_df.iterrows():
	for index1, row2 in positive_df.iterrows():
		#if index != index1:
		if iterations <= 10:
			if row['target'] == -1 and row2['target'] == -1:
				#temp = []
				#print type(np.asscalar(index)), index1
				#temp.append(np.asscalar(index))
				#temp.append(np.asscalar(index1))
				score = untruthful.score(row['review'],row2['review'])
				print score
				#temp.append(score)
				file1.write("'{0}','{1}','{2}'".format( np.asscalar(index),np.asscalar(index1),score))
				iterations += 1
		else:
			break
'''
	A random test case
'''	
review1 = "I love this product"
review2 = "I like this product"
print untruthful.score(review1,review2)


target = []
for i in negative_df.index:
	if ((negative_df['labeled_class'][i] == 'negative') & (negative_df['actual_class'][i] == 't')):
		target.append(1)
	elif ((negative_df['labeled_class'][i] == 'negative') & (negative_df['actual_class'][i] == 'd')):
		target.append(-1)
	else:
		print "Error"
negative_df['target'] = target

data = positive_df.merge(negative_df,how='outer')
data = data[['review','target']]


'''
	Implementation of Perl's Autovivification feature.
	Possible data structure for R in P_semantic.
'''

class AutoVivification(dict):
	def __getitem__(self, item):
		try:
			return dict.__getitem__(self, item)
		except KeyError:
			value = self[item] = type(self)()
			return value
