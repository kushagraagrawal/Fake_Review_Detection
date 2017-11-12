'''
	Script containing the class with all the features used by the classifier to classify reviews as genuine or duplicitous.
	The features used have been shown effective to detect web spam in general (Piskorski et al. 2008).
	To use the features of the class, just make an object of the class and call the function add_features with your text. 
	Syntax-
			<object_name>.add_features(<text>)
'''

'''
	Dependencies of the class. The different libraries used - 
	1> NLTK
	2> JSON
	3> RE (regular expressions)
	4> ENCHANT
	5> MATH
	6> PANDAS
	7> SYS
'''
import nltk
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
import json
from nltk.corpus import brown
import re
import enchant
from nltk.collocations import *
from collections import Counter
import math
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
from pandas.io.json import json_normalize
from sys import argv

'''
	Project aim - To give a probabilistic rating to how fake a review is
	Features used have been shown effective to detect web spam in general (Piskorski et al. 2008)
'''
'''
	POS tag list
	
    CC coordinating conjunction
    CD cardinal digit
    DT determiner
    EX existential there (like: "there is" ... think of it like "there exists")
    FW foreign word
    IN preposition/subordinating conjunction
    JJ adjective 'big'
    JJR adjective, comparative 'bigger'
    JJS adjective, superlative 'biggest'
    LS list marker 1)
    MD modal could, will
    NN noun, singular 'desk'
    NNS noun plural 'desks'
    NNP proper noun, singular 'Harrison'
    NNPS proper noun, plural 'Americans'
    PDT predeterminer 'all the kids'
    POS possessive ending parent's
    PRP personal pronoun I, he, she
    PRP$ possessive pronoun my, his, hers
    RB adverb very, silently,
    RBR adverb, comparative better
    RBS adverb, superlative best
    RP particle give up
    TO to go 'to' the store.
    UH interjection errrrrrrrm
    VB verb, base form take
    VBD verb, past tense took
    VBG verb, gerund/present participle taking
    VBN verb, past participle taken
    VBP verb, sing. present, non-3d take
    VBZ verb, 3rd person sing. present takes
    WDT wh-determiner which
    WP wh-pronoun who, what
    WP$ possessive wh-pronoun whose
    WRB wh-abverb where, when

'''
class FeatureClass:
	'''
		Possible constants for a constructor.
	'''
	uid = 0.0
	title = ""
	content = ""
	star = {'rating':0.0,'base':0.0}
	average_rating = {'rating':0.0,'base':0.0}
	name_of_reviewer = ""
	location = []
	#time_of_review
	Photoavailable = False
	email_address = ""
	pos_bigrams = []
	'''
	def __init__(uid, title, content, star, average_rating, name_of_reviewer, location, Photoavailable, email_address):
		self.uid = uid
		self.title = title
		self.content = content
		self.star = star
		self.average_rating = average_rating
		self.name_of_reviewer = name_of_reviewer
		self.location = location 
		self.Photoavailable = Photoavailable
		self.email_address = email_address
	'''	
	'''
		Helper functions
	'''
	
	'''
		Function to vectorize a text.
		Input: a review (text)
		Output: a list of words in text. Removes punctuation and common words according to NLTK Stopwords.
	'''
	
	def vectorize_text(self,text):
		def remove_punctuation(text):
			return re.sub('[,.?";:\-!@#$%^&*()]', '', text)
		def remove_common_words(text_vector):
			common_words = set(stopwords.words('english'))
			common_words = common_words - set(['him','his','herself','she','hers','her','himself','he','me','myself','my'])
			#print common_words
			return [word for word in text_vector if word not in common_words]
		
		#text = text.lower()
		#print text
		text = remove_punctuation(text)
		#print text
		words_list = text.split()
		words_list = remove_common_words(words_list)
		#print words_list
		return words_list
	
	'''
		Function for tagging the terms with Parts Of Speech based on NLTK POS Tagging.
		Input: The review for tagging
		Output: List of Tuples containing the term at its POS tag.
	'''
	
	def pos_tagging(self,text):
		#textvector = nltk.sent_tokenize(text)
		textvector = self.vectorize_text(text)
		#print textvector
		POS_tagger = nltk.pos_tag(textvector)
		#POS_tagger = nltk.pos_tag_sents([nltk.word_tokenize(s) for s in textvector])
		return POS_tagger
	
	'''
		Function to convert the JSON file to pandas DataFrame. Takes a review, adds all the features and returns the DataFrame
		Input: jsonfile name
		Output: Pandas DataFrame containing features of each review.
		
	'''
	
	def json_to_pddata(self,jsonfile):
		json_text = json.load(jsonfile)
		#b = pd.DataFrame(json_text)
		features = []
		index = 1
		for items in json_text:
			if index <= 20000:
				features.append(self.add_features(items['content']))
				index += 1
			else:
				break
		df = pd.DataFrame(features)
		return df
	
	'''
		Function to add features to the review to add to the DataFrame.
		Input: The review
		Output: dictionary containing features wrt the content for the DataFrame.
	'''	 
	
	def add_features(self,content):
		feature_vector = {}
		feature_vector["percentnouns"] = self.percentnouns(content)
		feature_vector["percentverbs"] = self.percentverbs(content)
		feature_vector["percentpronouns"] = self.percentpronouns(content)
		feature_vector["modalverbsratio"] = self.modalverbsratio(content)
		feature_vector["capitalized_diversity"] = self.capitalized_diversity(content)
		feature_vector["repeated_tokens"] = self.repeated_tokens(content)
		feature_vector["emotiveness_diversity"] = self.emotiveness_diversity(content)
		feature_vector["spelling_check"] = self.spelling_check(content)
		feature_vector["self_reference_diversity"] = self.self_reference_diversity(content)
		#feature_vector["lexical_validity"] = self.lexical_validity(content)
		feature_vector["text_orientation"] = self.text_orientation(content)
		feature_vector["sentiment_orientation"] = self.sentiment_orientation(content)
		feature_vector["lexical_diversity"] = self.lexical_diversity(content)
		feature_vector["content_diversity"] = self.content_diversity(content)
		feature_vector["pos_n_grams_diversity"] = self.pos_n_grams_diversity(content)
		feature_vector["lexical_entropy"] = self.lexical_entropy(content)
		return feature_vector
	
	'''
		Syntactical features
	'''	
	
	'''
		Function to find the percentage of nouns in a review.
		Calls the function pos_tagging to vectorize the review and tag the terms with Part of Speech tags. 
		Input: Review in question
		Output: percentage of nouns in a review
	'''
	
	def percentnouns(self,text):
		vectorised_text = self.pos_tagging(text)
		nouns = 0
		for i, (a,b) in enumerate(vectorised_text):
			if b == 'NN' or b == 'NNS' or b == 'NNP' or b == 'NNPS':
				#print b
				nouns += 1
		#print nouns
		try:
			return (float)(nouns)/(float)(len(vectorised_text))
		except ZeroDivisionError:
			return 0
	
	'''
		Function to find the percentage of verbs in a review.
		Calls the function pos_tagging to vectorize the review and tag the terms with Part of Speech tags. 
		Input: Review in question
		Output: percentage of verbs in a review
	'''		
	
	def percentverbs(self,text):
		vectorised_text = self.pos_tagging(text)
		verb = 0
		for i, (a,b) in enumerate(vectorised_text):
			if b == 'VB' or b == 'VBD' or b == 'VBG' or b == 'VBN' or b == 'VBP' or b == 'VBZ':
				verb += 1
		try:
			return (float)(verb)/(float)(len(vectorised_text))
		except ZeroDivisionError:
			return 0
	
	'''
		Function to find the percentage of pronouns in a review.
		Calls the function pos_tagging to vectorize the review and tag the terms with Part of Speech tags. 
		Input: Review in question
		Output: percentage of pronouns in a review
	'''		
	
	def percentpronouns(self,text):
		vectorised_text = self.pos_tagging(text)
		pronoun = 0
		for i, (a,b) in enumerate(vectorised_text):
			if b == 'PRP' or b == 'PRP$':
				pronoun += 1
		#print pronoun
		try:
			return (float)(pronoun)/(float)(len(vectorised_text))
		except ZeroDivisionError:
			return 0
	
	'''
		Function to find the ratio of modals to verbs in a review.
		Calls the function pos_tagging to vectorize the review and tag the terms with Part of Speech tags. 
		Input: Review in question
		Output: ratio of modals to verbs in a review
	'''
			
	def modalverbsratio(self,text):
		vectorised_text = self.pos_tagging(text)
		modals = 0
		verbs = 0
		for i,(a,b) in enumerate(vectorised_text):
			if b == 'MD':
				modals += 1
			elif b == 'VB' or b == 'VBD' or b == 'VBG' or b == 'VBN' or b == 'VBP':
				verbs += 1
		try:
			return (float)(modals)/(float)(verbs)
		except ZeroDivisionError:
			return 0
	
	'''
		Stylistic Features
	'''
	
	'''
		Function to calculate the ratio of words with first letter caps to all the words in a review.
		The function vectorizes the text and then calculates the ratio.
		Input: The Review in question
		Output: The ratio of words with first letter caps to all the words
	'''
	
	def capitalized_diversity(self,text):
		vectorised_text = self.vectorize_text(text)
		caps = 0.0
		for tokens in vectorised_text:
			if tokens[0].isupper():
				caps += 1.0
				#print tokens
		try:
			return (float)(caps)/(float)(len(vectorised_text))
		except ZeroDivisionError:
			return 0
	
	'''
		Function for calculating the ratio of repeated tokens to all the tokens in the review.
		The function vectorizes the text and then calculates the ratio.
		Input: The Review in question
		Output: The ratio of repeated tokens to all the tokens in the review
	'''
	
	def repeated_tokens(self,text):
		vectorised_text = self.vectorize_text(text)
		temp = set(vectorised_text)
		#print temp
		try:
			return (float)(len(vectorised_text) - len(temp))/(float)(len(vectorised_text))
		except ZeroDivisionError:
			return 0
	
	'''
		Function to calculate the ratio of number of adjectives + adverbs to the number of verbs and nouns.
		The function vectorizes the text and then calculates the ratio.
		Input: The Review in question
		Output: The ratio of (adjectives + adverbs) to (nouns + verbs)
	'''
			
	def emotiveness_diversity(self,text):
		pos_text = self.pos_tagging(text)
		adjectives = 0
		adverbs = 0
		nouns = 0
		verb = 0
		for i,(a,b) in enumerate(pos_text):
			if b == 'VB' or b == 'VBD' or b == 'VBG' or b == 'VBN' or b == 'VBP' or b == 'VBZ':
				verb += 1
			elif b == 'NN' or b == 'NNS' or b == 'NNP' or b == 'NNPS':
				nouns += 1
			elif b == 'JJ' or b == 'JJS' or b == 'JJR':
				adjectives += 1
			elif b == 'RB' or b == 'RBS' or b == 'RBR':
				adverbs += 1
		#print adjectives + adverbs
		try:
			return (float)(adjectives + adverbs)/(float)(verb + nouns)
		except ZeroDivisionError:
			return 0
	
	'''
		Function to calculate the ratio of spelling errors to the number of words in the review. Uses the python enchant library.
		If a word doesn't exist in the dictionary, it is assumed to be an error. Nouns are excluded of course.
		Input: The review in question
		Output: The ratio of spelling errors to number of words.
	'''
	
	def spelling_check(self,text):
		d = enchant.Dict("en_GB")
		list_of_words = self.pos_tagging(text)
		errors = 0
		for i,(a,b) in enumerate(list_of_words):
			if d.check(a) == False:
				if (b == 'NN' or (b == 'NNS' or (b == 'NNP' or (b == 'NNPS')))):
					continue
				else:
					errors += 1
		try:
			return (float)(errors)/(float)(len(list_of_words))
		except ZeroDivisionError:
			return 0
	
	'''
		Function to calculate the ratio of Personal Pronouns to the number of pronouns in a review.
		The function vectorizes the text and then calculates the ratio.
		Input: The Review in question
		Output: The ratio of Personal Pronouns to the number of Pronouns
	'''
			
	def self_reference_diversity(self,text):
		pos_text = self.pos_tagging(text)
		personal_pronoun = 0
		for i, (a,b) in enumerate(pos_text):
			if b == 'PRP':
				personal_pronoun += 1
		pronoun = 0
		for i, (a,b) in enumerate(pos_text):
			if b == 'PRP' or b == 'PRP$':
				pronoun += 1
		try:
			return (float)(personal_pronoun)/(float)(pronoun)
		except ZeroDivisionError:
			return 0
	'''
		Lexical Features
	'''
	
	'''
		Function to calculate the Lexical Validity. Ratio of the number of valid words to the number of all words in a review,
		with valid words defined with respect to WordNet. Here if the word has a synonym set, it is a valid set. Synonym sets taken from
		NLTK's WordNet.
		Input: The review in question.
		Output: Ratio of the number of valid words to the number of all words.
	'''
	
	def lexical_validity(self,text):
		
		list_of_words = self.vectorize_text(text)
		valid = 0
		for word in list_of_words:
			sysnet = wn.synsets(word)
			if len(sysnet) >= 0:
				valid += 1
		try:
			return (float)(valid) / (float)(len(list_of_words))
		except ZeroDivisionError:
			return 0
	
	'''
		Function to calculate the Text orientation.Text orientation is the ratio of the number of potential words to the
		number of all words in a review, where a potential word is a token that does not contain numbers, special characters,
		or non-letter symbols.
		Uses isalpha() function to check if word has all alphabets or not.
		Input: The review in question
		Output: The text orientation.	
	'''
	
	def text_orientation(self,text):
		vectorised_text = self.vectorize_text(text)
		illegal = 0
		for words in vectorised_text:
			#if set('[~!@#$%^&*()_+{}":;\']+$').intersection(words):
			#	if any(char.isdigit() for char in words):
			#		illegal += 1
			if words.isalpha() == False:
				#print words
				illegal += 1
		try:
			return (float)(len(vectorised_text) - illegal)/(float)(len(vectorised_text))
		except ZeroDivisionError:
			return 0
	
	'''
		Function to find the reviews polarity. Uses NLTK's Vader Intensity Analyzer to find the polarity of the sentence. Positive polarity indicates positive sentiment and negative indicates negative sentiment.
		Neutral is given 0 score.
		Input: The review in question
		Output: The polarity of the review. Takes average of all the sentences' polarity.
	'''
			
	def sentiment_orientation(self,text):
		lines_list = nltk.sent_tokenize(text)
		sid = SentimentIntensityAnalyzer()
		temp = 0.0
		for sentence in lines_list:
			#print sentence
			ss = sid.polarity_scores(sentence)
			temp += ss['compound']
		try:
			return temp/(float)(len(lines_list))
		except ZeroDivisionError:
			return 0
	
	'''
		Function to find the lexical diversity in a review. Lexical diversity is the ratio of the
		number of unique words to the number of all words in the review.
		Input: Review in question
		Output: Ratio of unique words to all the words.
	'''
	
	def lexical_diversity(self,text):
		list_of_words = text.split()
		unique_words = set(list_of_words)
		#print unique_words
		try:
			return (float)(len(unique_words))/(float)(len(list_of_words))
		except ZeroDivisionError:
			return 0
	
	'''
		Function to find the content diversity in a review. Content diversity is the ratio of
		the number of unique nouns and unique verbs to the number of all nouns and verbs presented in a review.
		Calls the function pos_tagging to vectorize the review and tag the terms with Part of Speech tags. 
		Input: The review in question
		Output: Ratio of (unique nouns + verbs) to the (nouns + verbs)
	'''
			
	def content_diversity(self,text):
		pos_text = self.pos_tagging(text)
		verb = 0
		noun = 0
		nouns =[]
		verbs = []
		for i,(a,b) in enumerate(pos_text):
			if b == 'VB' or b == 'VBD' or b == 'VBG' or b == 'VBN' or b == 'VBP' or b == 'VBZ':
				verb += 1
				nouns.append(a)
			elif b == 'NN' or b == 'NNS' or b == 'NNP' or b == 'NNPS':
				noun += 1
				verbs.append(a)
		nouns = set(nouns)
		verbs = set(verbs)
		try:
			return (float)(len(nouns) + len(verbs))/(float)(noun + verb)
		except ZeroDivisionError:
			return 0
		# ratio of unique nouns, verbs to number of all nouns and verbs
	
	'''
		Function to find the diversity of POS bigrams. POS bigrams have the form (noun, verb), (adjective, noun), (adverb, adjective), etc.
		POS bigram diversity is the ratio of the number of different POS bigrams to the total number of POS bigrams.
		Calls the function pos_tagging to vectorize the review and tag the terms with Part of Speech tags. 
		Input: The review in question
		Output: ratio of the number of different POS bigrams to the total number of POS bigrams.
	'''
	
	def pos_n_grams_diversity(self,text):
		def remove_punctuation(text):
			return re.sub('[,.?";:\-!@#$%^&*()]', '', text)
		
		bigram_measures = nltk.collocations.BigramAssocMeasures()
		text = remove_punctuation(text)
		tokens = nltk.wordpunct_tokenize(text)
		finder = BigramCollocationFinder.from_words(tokens)
		scored = finder.score_ngrams(bigram_measures.raw_freq)
		bigrams = sorted(bigram for bigram, score in scored)
		
		'''
			more efficient way for this
		'''
		for i, (a,b) in enumerate(bigrams):
			c = nltk.pos_tag([a])
			d = nltk.pos_tag([b])
			c = dict(c)
			d = dict(d)
			#print c.values(), d.values()
			self.pos_bigrams.append(tuple((c.values()[0],d.values()[0])))
		try:
			return (float)(len(set(self.pos_bigrams)))/(float)(len(self.pos_bigrams))
		except ZeroDivisionError:
			return 0
	
	'''
		Function to calculate lexical entropy.
		Input - text
		Output - lexical entropy
	'''
	
	def lexical_entropy(self,text):
		
		d = {}
		frequencies = Counter(elem for elem in self.pos_bigrams)
		for key, value in frequencies.items():
			d[key] = value
		sum1 = 0
		for key,value in d.iteritems():
			sum1 += -(((float)(value)/(float)(len(self.pos_bigrams))) * math.log((float)(value)/(float)(len(self.pos_bigrams)),2))
			#print key, value, len(self.pos_bigrams)
			#print ((float)(value)/(float)(len(self.pos_bigrams)))
			#print math.log((float)(value)/(float)(len(self.pos_bigrams)),2)
			#print math.log((float)(value)/(float)(len(self.pos_bigrams)),10)
			#print '\n'
		return sum1
#something = FeatureClass()
#jsonfile = open(argv[1],'r')
#json_text = json.load(jsonfile)
#text = json_text[2]['content']
#print something.pos_n_grams_diversity(text)
#print something.lexical_entropy(text)
#print something.text_orientation(text)
#print something.json_to_pddata(jsonfile)		
