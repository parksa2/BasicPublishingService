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
6. Run 'chalice local' which would bind to port 8000 and proceed to test resources. 

Developed on Python 2.7.14. Tested and deployed on Windows 10.

API documentation.

1. API status.

Method:GET URL: /status No URL params.

This resource checks the availablity of other resources. It returns a json object with two properties, newsStatus and awsStatus. 
If there is a problem with accessing one or both of the appropriate resources, because of an invalid api key or invalid bucket, this will be reflected in
the status call. For example if the access key in the config is invalid but everything else in the config worked, the status call will return
{
    "newsStatus": "Good",
    "awsStatus": "An error occurred (403) when calling the HeadBucket operation: Forbidden"
}

The methodology for status checking depends on the resource. 

The newsStatus is determined by any errors by doing a single query to the news API of a single news source. The news API provides its own status and message params, if the status is an error, the newsStatus changes to the message from the API. 

The aws status is determined by making a head_bucket call on the boto3 client with the bucket provided in the config. If for whatever reason the user cannot access that bucket, the aws status is changed from good to whatever the exception thrown.

2. Transform publicly available data into something fun.

Method:GET URL: /topNewsWords Optional URL params: 'maxWordCount', 'minWordLen'

This resource maps the top words by usage from a number of sources in the news API. It uses a subclass of a python dictionary to keep track of the appearance of each word called a counter. The function loops through all the sources in the newsAPI object, sources field calling each for the top news. Then for each article, it parses the title of each article into seperate words and adds each word to the counter object if they don't exist with a count of 1 or it would add one to its current value with that word as a key, if the wordsize is greater than or equal to the minWordLen. minWordLen determines the minimum word size to be considered in the counter object. If its less than the midLen, it won't be added. After building the counter object, it returns only the most common determined by the counter function most_common and the optional input maxWordCount. The default for both maxWordCount and minWordLen is set by the config.

The call /topNewsWords?maxWordCount=2&minWordLen=4 might return 

[
    [
        "deal",
        6
    ],
    [
        "trump",
        6
    ]
]

The exact result would depend on the news provided by the api.

3. Upload a PNG image to S3.

Method: PUT URL: /upload/{fileName}  Headers: content-type: "multipart/form-data". Body: a .png file

This resource uploads a file onto S3 with the fileName param as its name. This functionality requires an existing AWS bucket with its name, private key and secret key in the config. Additionally, it must be configured to set up static website hosting already, where the index page file name is set in the config and is the same as defined in the webhost.

This resource works by taking the file uploaded in the body, creating a new temporary file with the provided fileName as its new name, then uploading it to the bucket. Then the resource generates an HTML file with the image file name and then uploads it to the bucket. The resource then returns the url displaying the image.


See the image on: https://s3.amazonaws.com/image.hosting.parks/index.html for an example request and response on Postman.

Where 'index': 'index.html' and 'bucketName': 'andrew.parks.chalice'

-
Ideas for improvement

A caching system on the top news resource, so that it doesn't make several API calls each time someone hits that resource. The news does not change that often, a singleton holding the counter object and only executing the API calls after a set amount of time has passed, busting the cache.

Programmatic creation of a bucket with the necessary permissions if required on the upload file resource. URL params for a user provided bucket instead of being hardcoded.

-

If you have any questions, please do not hesitate to email me at parksa243@gmail.com 