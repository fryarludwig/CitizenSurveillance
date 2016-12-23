# -*- coding: utf-8 -*-
import requests
import json
import codecs
import sys, time
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class WatsonWord:
    def __init__(self):
        self.display_as  = "TCP/IP"
        self.sounds_like = ["T. C. P. I. P."]
        self.count       = 1
        self.source      = ["user"]
        self.word        = "tcpip"

class Credentials:
    def __init__(self, auth_json):
        self.headers = auth_json['headers']
        self.username = auth_json['username']
        self.password = auth_json['password']
        self.url = auth_json['url']
        self.uri = auth_json['uri']

    def __str__(self):
        return 'Header:   {}\n' \
               'User:     {}\n' \
               'Password: {}\n' \
               'Url:      {}\n' \
               'Custom:   {}'.format(self.headers,self.username, self.password, self.url, self.uri)

class WatsonInterface:
    def __init__(self):
        self.auth = Credentials(json.load(open('./settings.json', 'r')))
        self.custom_id = "Test_Scanner_1"
        self.corpus_name = "corpus.txt"

    def __str__(self):
        return str(self.auth)

    def Post(self, destination, payload=None, verify=False):
        print "Posting: {}".format(destination)
        resp = requests.post(destination, auth=(self.auth.username, self.auth.password), verify=verify,
                             headers=self.auth.headers, data=payload)
        print "Response: {}".format(resp)
        return resp

    def Get(self, destination, payload=None, verify=False):
        print "Getting: {}".format(destination)
        resp = requests.get(destination, auth=(self.auth.username, self.auth.password), verify=verify,
                             headers=self.auth.headers, data=payload)
        print "Response: {}".format(resp)
        return resp

    def Put(self, destination, payload=None, verify=False):
        print "Putting: {}".format(destination)
        resp = requests.put(destination, auth=(self.auth.username, self.auth.password), verify=verify,
                             headers=self.auth.headers, data=payload)
        print "Response: {}".format(resp)
        return resp

    def CreateModel(self, name, description, base_model="en-US_BroadbandModel"):
        ##########################################################################
        # Step 1: Create a custom model
        # Change "name" and "description" to suit your own model
        ##########################################################################
        print "\nCreating custom mmodel..."
        data = {"name": name, "base_model_name": base_model, "description": description}
        jsonObject = json.dumps(data).encode('utf-8')
        resp = self.Post(self.auth.uri, jsonObject)

        if resp.status_code != 201:
            print "Failed to create model"
            print resp.text
            sys.exit(-1)

        respJson = resp.json()
        self.custom_id = respJson['customization_id']
        print "Model customization_id: ", self.custom_id

    def AddCorpusFile(self, corpus_file='./corpus.txt', corpus_name='cachecountcoprus'):
        ##########################################################################
        # Step 2: Add a corpus file (plain text file - ideally one sentence per line,
        # but not necessary). In this example, we name it 'corpus1' - you can name
        # it whatever you want (no spaces) - if adding more than one corpus, add
        # them with different names
        ##########################################################################
        print "\nAdding corpus file..."
        uri = self.auth.uri + "/" + self.custom_id + "/corpora/" + corpus_name
        self.corpus_name = corpus_name

        with open(corpus_file, 'rb') as f:
            r = self.Post(uri, f)

        if r.status_code != 201:
            print "Failed to add corpus file"
            print r.text

    def CheckCorpusStatus(self):
        ##########################################################################
        # Step 3: Get status of corpus file just added.
        # After corpus is uploaded, there is some analysis done to extract OOVs.
        # One cannot upload a new corpus or words while this analysis is on-going so
        # we need to loop until the status becomes 'analyzed' for this corpus.
        ##########################################################################
        print "Checking status of corpus analysis..."
        uri = self.auth.uri + "/" +  self.custom_id + "/corpora/" + self.corpus_name
        r = self.Get(uri)
        respJson = r.json()
        status = respJson['status']
        time_to_run = 10
        while (status != 'analyzed'):
            time.sleep(10)
            r = self.Get(uri)
            respJson = r.json()
            status = respJson['status']
            print "status: ", status, "(", time_to_run, ")"
            time_to_run += 10
        print "Corpus analysis done!"

    def ShowOOVs(self):
        ##########################################################################
        # Show all OOVs found
        # This step is only necessary if user wants to look at the OOVs and
        # validate the auto-added sounds-like field. Probably a good thing to do though.
        ##########################################################################
        print "\nListing words..."
        uri = self.auth.uri + "/" + self.custom_id + "/words?sort=count"
        r = self.Get(uri)
        print "Listing words returns: ", r.status_code
        file = codecs.open("output.OOVs.corpus", 'wb', 'utf-8')
        file.write(r.text)
        print "Words list from added corpus saved in file: output.OOVs.from-corpus"

    def AddWord(self):
        ##########################################################################
        # Step 4: Add a single user word
        # One can pass sounds_like and display_as fields or leave empty (if empty
        # the service will try to create its own version of sounds_like)
        ##########################################################################
        print "\nAdding single word..."
        data = {"sounds_like": ["T. C. P. I. P."], "display_as": "TCP/IP"}
        wordToAdd = "tcpip"
        u = unicode(wordToAdd, "utf-8")
        uri = self.auth.uri + self.custom_id + "/words/" + u
        jsonObject = json.dumps(data).encode('utf-8')
        r = self.Put(uri, jsonObject)
        print "Single word added!"

        # Alternatively, one can add multiple words in one request
        print "\nAdding multiple words..."
        data = {"words": [{"word": "IEEE", "sounds_like": ["I. triple E."], "display_as": "IEEE"},
                          {"word": "hhonors", "sounds_like": ["H. honors", "hilton honors"], "display_as": "HHonors"}]}
        uri = "https://stream.watsonplatform.net/speech-to-text/api/v1/customizations/" + self.custom_id + "/words"
        jsonObject = json.dumps(data).encode('utf-8')
        r = self.Post(uri, jsonObject)

        print "Adding multiple words returns: ", r.status_code

    def GetModelStatus(self):
        ##########################################################################
        # Get status of model - only continue to training if 'ready'
        ##########################################################################
        uri = self.auth.uri + "/" + self.custom_id
        r = self.Get(uri)
        respJson = r.json()
        print respJson
        status = respJson['status']
        print "Checking status of model for multiple words..."
        time_to_run = 10
        while (status != 'ready'):
            time.sleep(10)
            r = self.Get(uri)
            respJson = r.json()
            status = respJson['status']
            print "status: ", status, "(", time_to_run, ")"
            time_to_run += 10

        print "Multiple words added!"
        # Show all words added so far
        print "\nListing words..."
        uri = self.auth.uri + "/" + self.custom_id + "/words?word_type=user&sort=alphabetical"
        r = self.Get(uri)
        file = codecs.open("output.OOVs.user", 'wb', 'utf-8')
        print r.text
        print r
        file.write(r.text)
        print "Words list from user-added words saved in file: output.OOVs.user"

    def StartTraining(self):
        ##########################################################################
        # Step 5: Start training the model
        # After starting this step, need to check its status and wait until the
        # status becomes 'available'.
        ##########################################################################
        print "\nTraining custom model..."
        uri = self.auth.uri + self.custom_id + "/train"
        data = {}
        jsonObject = json.dumps(data).encode('utf-8')
        r = self.Post(uri, jsonObject)
        if r.status_code != 200:
            print "Training failed to start - exiting!"
            sys.exit(-1)

    def UpdateTrainingStatus(self):
        ##########################################################################
        # Get status of training and loop until done
        ##########################################################################
        uri = self.auth.uri + self.custom_id
        r = self.Get(uri)
        respJson = r.json()
        status = respJson['status']
        time_to_run = 10
        while (status != 'available'):
            time.sleep(10)
            r = self.Get(uri)
            respJson = r.json()
            status = respJson['status']
            print "status: ", status, "(", time_to_run, ")"
            time_to_run += 10
        print "Training complete!"

        print "\nGetting custom models..."
        uri = self.auth.uri
        r = self.Get(uri)
        print r.text
        sys.exit(0)

    def DeleteModel(self):
        ##########################################################################
        # STEP 6 (OPTIONAL): TO LIST AND DELETE THE CUSTOM MODEL:
        # Comment the previous call to 'sys.exit(0)'; useful for experimentation
        # with multiple test models
        ##########################################################################
        print "\nDeleting custom model..."
        uri = "https://stream.watsonplatform.net/speech-to-text/api/v1/customizations/" + self.custom_id
        r = self.Get(uri)
        print "\nGetting custom models..."
        uri = "https://stream.watsonplatform.net/speech-to-text/api/v1/customizations/"
        r = self.Get(uri)
        sys.exit(0)

if False and __name__ == '__main__':
    print 'Hello world'
    test_watson = WatsonInterface()
    test_watson.CreateModel("Test_Scanner_2", "First model to test scanner customization")
    test_watson.AddCorpusFile()
    test_watson.ShowOOVs()
    test_watson.GetModelStatus()
    test_watson.DeleteModel()

    exit(0)
