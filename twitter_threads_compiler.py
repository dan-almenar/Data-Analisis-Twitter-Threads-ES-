import tweepy
import os
import csv
#import datetime
import time



#Twitter initializer
CONSUMER_KEY = 'twitter probided key for your account' #get yours at http://developer.twitter.com
CONSUMER_SECRET = 'twitter probided key for your account'
ACCESS_KEY = 'twitter probided key for your account'
ACCESS_SECRET = 'twitter probided key for your account'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)

api = tweepy.API(auth)


#twitter thread class with the parameters that will be analized
class TwitterThread():
	def __init__(self, topic, last_thread_tweet_id):
		self.last_thread_tweet_id = last_thread_tweet_id
		self.name = topic
		self.tweets_ids = []
		self.lenght = 0
		self.created_at = ''
		self.total_likes = 0
		self.total_retweets = 0
		self.total_interactions = 0
		self.average_likes = 0
		self.average_retweets = 0
		self.average_interactions = 0
		self.thread_text = ''
		self.each_tweet_data = []

		self.get_thread_ids(last_thread_tweet_id)


	def get_thread_ids(self, last_thread_tweet_id):
		print(f'Creating {self.name} TwitterThread object...')
		last_thread_tweet = api.get_status(id=str(last_thread_tweet_id))
		thread_tweets_ids = []
		previous_tweet = last_thread_tweet
		
		while previous_tweet.in_reply_to_status_id:
			thread_tweets_ids.append(previous_tweet.id)
			previous_tweet = api.get_status(id=previous_tweet.in_reply_to_status_id)
			if previous_tweet.in_reply_to_status_id == None:
				thread_tweets_ids.append(previous_tweet.id)
				self.created_at = previous_tweet.created_at
			
		thread_tweets_ids.sort()
		self.tweets_ids = thread_tweets_ids
		self.lenght = len(thread_tweets_ids)
			
		self.reconstruct_thread_text(self.tweets_ids)
		self.get_interactions(self.tweets_ids)
			

	def reconstruct_thread_text(self, tweets_ids):
		print("Reconstructing thread's text...")
		full_text = ''
		for tweet in self.tweets_ids:
			tweet_text = api.get_status(id=tweet).text
			if full_text == '':
				full_text = full_text + tweet_text
			else:
				full_text = full_text + '\n' + tweet_text
		
		self.thread_text = full_text
		return self.thread_text 


	def get_interactions(self, tweets_ids):
		print("Processing thread's interactions...")
		total_likes = 0
		total_retweets = 0
		average_likes = 0
		average_retweets = 0
		for tweet in self.tweets_ids:
			#process likes
			likes = api.get_status(id=(tweet)).favorite_count
			total_likes += likes
			
			#process retweets
			retweets = api.get_status(id=(tweet)).retweet_count
			total_retweets += retweets
			
			#get tweet text
			text = api.get_status(id=(tweet)).text
			
			#compiling each tweet's data for thread's csv file:
			tweet_data = {'Tweet ID' : tweet,
									'Text' : text,
									'Likes' : likes,
									'Retweets' : retweets,
									'Total Interactions' : likes + retweets}
			self.each_tweet_data.append(tweet_data)
			
			#totalizing
		self.total_likes = total_likes
		self.total_retweets = total_retweets
		self.total_interactions = total_likes + total_retweets
		self.average_likes = int(self.total_likes / len(tweets_ids))
		self.average_retweets = int(total_retweets / len(tweets_ids))
		self.average_interactions = int(self.total_interactions / len(tweets_ids))
			
		return

'''
data will be stored in two separated csv files:
	1. The dataset file will hold data for a full set of twitter threads:
		The function scans the path for the dataset file.
			If it doesn't exist, gets created and the header gets written before appending the thread's data.
			If it already exists, it just appends the thread's data.
	2. The thread_data_file will hold data just from each tweet of the given TwitterThread object.		
'''

# dataset file:
def write_to_dataset(TwitterThread):
	thread = TwitterThread
	path = os.getcwd()
	dataset = 'threads_dataset.csv'
	dataset_fieldnames = ['Topic', 'created at:', 'lenght', 'Total Likes', 'Average Likes',
							'Total Retweets', 'Average Retweets', 'Total Interactions', 'Average Interactions']
	dataset_data = {'Topic' : thread.name, 
								'created at:' : thread.created_at, 
								'lenght' : thread.lenght, 
								'Total Likes' : thread.total_likes,
								'Average Likes' : thread.average_likes, 
								'Total Retweets' : thread.total_retweets, 
								'Average Retweets' : thread.average_retweets,
								'Total Interactions' : thread.total_interactions,
								'Average Interactions' : thread.average_interactions,}
	if dataset not in os.listdir(path):
		print('Creating Twitter Threads dataset...')
		with open(dataset, 'a+') as dataset_file:
			dataset_writer = csv.DictWriter(dataset_file, fieldnames=dataset_fieldnames)
			dataset_writer.writeheader()
			dataset_writer.writerow(dataset_data)
	else:
		print(f'Dataset found, appending {thread.name} data...')
		with open(dataset, 'a+') as dataset_file:
			dataset_writer = csv.DictWriter(dataset_file, fieldnames=dataset_fieldnames)
			dataset_writer.writerow(dataset_data)

	print(f'Succesfully added {thread.name} data to the dataset.')
	return


# thread data file:
def write_thread_data(TwitterThread):
	thread = TwitterThread
	thread_file = f'{thread.name}.csv'
	thread_fieldnames = ['Tweet ID', 'Text', 'Likes', 'Retweets', 'Total Interactions']
	with open(thread_file, 'w') as thread_csv:
		thread_csv_writer = csv.DictWriter(thread_csv, fieldnames=thread_fieldnames)
		thread_csv_writer.writeheader()
		for tweet_data in thread.each_tweet_data:
			thread_csv_writer.writerow(tweet_data)
	
	print(f'Succesfully created {thread.name} data file.')
	return

#LaSirenita = TwitterThread('La Sirenita', '1269050952373415938')

#LaBellaDurmiente = TwitterThread('La Bella Durmiente', '1269777501724782598')

#Blancanieves = TwitterThread('Blancanieves', '1271616826951307265')

#LaCenicienta = TwitterThread('La Cenicienta', '1272284701949071360')

#LaBellaYLaBestia = TwitterThread('La Bella y La Bestia', '1274444083054940160')

#Frozen = TwitterThread('La Reina de las Nieves (Frozen)', '1275275835059077120')

#Pocahontas = TwitterThread('Pocahontas', '1277088288776638464')

#Alicia = TwitterThread('Alicia en el Pais de las Maravillas', '1279887396058824704')

#Pinocho = TwitterThread('Pinocho', '1282532665124687872')

#Mulan = TwitterThread('Mulan', '1284708969999630338')

#Moana = TwitterThread('Moana', '1287471205159776257')

#Rapunzel = TwitterThread('Rapunzel', '1290047136365596673')

#PeterPan = TwitterThread('Peter Pan', '1292801641662615552')

#PrincesaYSapo = TwitterThread('La Princesa y el sapo', '1295153354667184133')

#Bambi = TwitterThread('Bambi', '1297965002524168193')

#CaperucitaRoja = TwitterThread('La Caperucita Roja', '1299899108229083137')

#PrincesaGuisante = TwitterThread('La Princesa y el guisante', '1302810771538276356')

#Tarzan = TwitterThread('Tarzan', '1304921155216838659')

#Anastasia_1 = TwitterThread('Anastasia pt. 1', '1310201584308060166')

#Anastasia_2 = TwitterThread('Anastasia pt. 2', '1310203782744113153')

#FlautistaHamelin = TwitterThread('El flautista de Hamelin', '1312743655309017088')

#ElDorado = TwitterThread('El Dorado', '1315826174564630534')

#HanselGretel = TwitterThread('Hansel y Gretel', '1318027490644865025')

#GatoConBotas = TwitterThread('El gato con botas', '1320525689393733634')

#JineteSinCabeza = TwitterThread('El jinete sin cabeza', '1322719252965658625')

#Rumpelstiltskin = TwitterThread('Rumpelstiltskin', '1328177071760281600')

#JorobadoNotreDame = TwitterThread('El jorobado de Notre Dame', '1335419230649520129')

