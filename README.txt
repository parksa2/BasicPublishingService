Instructions to install and run

1. Git clone https://github.com/parksa2/BasicPublishingService.git
2. Create a virtual python environment inside the root directory.
3. Install the requirements in the requirements.txt folder located in the {root}/BasicPublishingService in the virtual environment.
4. Run 'chalice local' from the {root}/BasicPublishingService. Chalice should run on localhost:8000. Resources will not crash but produce error messages without a populated config file
5. Populate the config file. 
	a. Go to https://newsapi.org/ and generate a free api key.
	b. Put the API key in the config file inside {root}/BasicPublishingService in as the value of the 'key' property of the newsConfig object.
	c. If lacking one already create an AWS s3 bucket configured to display a static website with a given html file.
	d. Put the name of the html file, access key, secret key and bucket name in the awsConfig object on the config.
6. Run 'chalice local' and proceed to test resources. 

If you have any questions, please do not hesitate to email me at parksa243@gmail.com 