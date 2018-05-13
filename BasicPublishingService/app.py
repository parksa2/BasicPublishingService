from chalice import Chalice, Response
from collections import Counter
import requests
import json
import re
import boto3
import os 
import config

app = Chalice(app_name='AdvanceDigital')
BUCKET = config.awsConfig['bucketName'] 
s3Client = boto3.client('s3', aws_access_key_id=config.awsConfig['accessKey'] , aws_secret_access_key=config.awsConfig['secretKey'] )

NEWS_URL = config.newsConfig['url']
API_KEY  = config.newsConfig['key']
SOURCES_LIST = config.newsConfig['sources']
app.debug = config.settings['debugMode']
DEFAULT_WORD_LIMIT = config.newsConfig['defaultWordLimit']
DEFAULT_MIN_WORD_LEN = config.newsConfig['defaultMinWordLen']
INDEX = config.awsConfig['index']

dirPath = os.path.dirname(os.path.realpath(__file__))

@app.route('/status')
def getStatus():
	awsStatus = "err"
	newsStatus = "err"
	try:
		s3Client.head_bucket(Bucket=BUCKET)
		awsStatus = "Good"
	except Exception as e:
		awsStatus = str(e)
	try: 
		url = NEWS_URL+SOURCES_LIST[0]+'&apiKey='+API_KEY
		r = requests.get(url)
		response = json.loads(r.content)
		if response['status'] == "error":
			newsStatus = response['message']
		else:
			newsStatus = "Good"
	except Exception as e:
		newsStatus = str(e)

	return Response(body={"awsStatus":awsStatus, "newsStatus":newsStatus})

@app.route('/upload/{fileName}', methods=['PUT'], content_types=['multipart/form-data'])
def uploadToS3(fileName):
	body = app.current_request.raw_body
	tmpFileName = dirPath+'/' + fileName
	with open(tmpFileName, 'wb') as file:
		file.write(body)
		file.close()
	index =  dirPath+'/'+INDEX
	try:
		s3Client.upload_file(tmpFileName, BUCKET, fileName, ExtraArgs={'ACL':'public-read'})
	except:
		return Response(body={'error': 'could not upload picture file to s3'}, status_code=500)
	imgUrl= 'https://s3.amazonaws.com/'+BUCKET+'/'+fileName

	with open(index, 'wb') as file:
		file.write('<!DOCTYPE html><html><body><img src="'+fileName+'"></body></html>')
		file.close()
	try:	
		s3Client.upload_file(index, BUCKET, INDEX, ExtraArgs={'ACL':'public-read', 'ContentType':'text/html'})
	except:
		return Response(body={'error': 'could not upload html file to s3'}, status_code=500)
	return Response(body={'AWS_URL': 'https://s3.amazonaws.com/'+BUCKET+'/'+INDEX}, status_code=200, headers={'Content-Type': 'application/json'})


@app.route('/topNewsWords')
def topNewsWords():
	totalData = []
	maxWordCount = DEFAULT_WORD_LIMIT
	minWordLen = DEFAULT_MIN_WORD_LEN
	req = app.current_request.to_dict()

	if req["query_params"]:
		params = req["query_params"]
		if 'maxWordCount' in params and params['maxWordCount'].isdigit():
			maxWordCount = int(params['maxWordCount'])
		if 'minWordLen' in params and params['minWordLen'].isdigit():
			minWordLen = int(params["minWordLen"])
	try:
		for source in SOURCES_LIST:
			url = NEWS_URL+source+'&apiKey='+API_KEY
			r = requests.get(url)
			jdata = json.loads(r.content)
			totalData = totalData +jdata['articles']
	except:
		return  Response(body={'error': 'There was a problem getting the news data'},status_code=500)

	return topWordsCounter(totalData,minWordLen).most_common(maxWordCount);

def topWordsCounter(totalData, minLen):
	dictionary = Counter()
	for item in totalData:
		if(item['title'] is not None):
			wordList = re.sub(r'[.!,;?]', ' ',item['title'].lower()).split()
			for word in wordList:
				if word in dictionary and len(word)>=minLen:
					dictionary[word]=dictionary[word]+1
				elif len(word)>=minLen:
					dictionary[word]=1
	return dictionary
