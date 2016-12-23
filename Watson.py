# -*- coding: utf-8 -*-
import requests
import json
import codecs
import sys, time
from LogUtility import *
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

WRITE_LOG_FILE = False
CURRENT_TIME = datetime.datetime.now().strftime('%Y_%m_%d-%H_%M')
LOGFILE_PATH = './Logs/Watson-{}-log.txt'.format(CURRENT_TIME)

class WatsonWord:
    def __init__(self):
        self.display_as  = "TCP/IP"
        self.sounds_like = ["T. C. P. I. P."]
        self.count       = 1
        self.source      = ["user"]
        self.word        = "tcpip"


class WatsonUtility:
    def __init__(self, settings, logger=None):
        self.headers = settings['headers'] if 'headers' in settings else ""
        self.username = settings['username'] if 'username' in settings else ""
        self.password = settings['password'] if 'password' in settings else ""
        self.base_url = settings['base_url'] if 'base_url' in settings else ""
        self.endpoint = settings['endpoint'] if 'endpoint' in settings else ""
        self.custom_id = "Test_Scanner_1"
        self.corpus_name = "corpus.txt"
        if logger is None:
            if WRITE_LOG_FILE:
                self.logger = LogUtility(LOGFILE_PATH)
            else:
                self.logger = LogUtility()
        else:
            self.logger = logger if logger is not None else LogUtility(LOGFILE_PATH)
        self.logger.Trace("Created WatsonUtility")

    @property
    def __str__(self):
        return 'User: {}\n' \
               'Pass: {}\n' \
               'Url:  {}\n' \
               'API:  {}'.format(self.username, self.password, self.base_url, self.endpoint)

    def Post(self, destination, payload=None, verify=False):
        self.logger.Trace("Posting: {}".format(destination))
        resp = requests.post(destination, auth=(self.username, self.password), verify=verify,
                             headers=self.headers, data=payload)
        self.logger.Trace("Response: {}".format(resp))
        return resp

    def Put(self, destination, payload=None, verify=False):
        self.logger.Trace( "Putting: {}".format(destination))
        resp = requests.put(destination, auth=(self.username, self.password), verify=verify,
                             headers=self.headers, data=payload)
        self.logger.Trace("Response: {}".format(resp))
        return resp

    def Get(self, destination, verify=False):
        self.logger.Trace( "Getting: {}".format(destination))
        resp = requests.get(destination, auth=(self.username, self.password), verify=verify,
                             headers=self.headers, data=payload)
        self.logger.Trace("Response: {}".format(resp))
        return resp

    def CreateModel(self, name, description, base_model="en-US_BroadbandModel"):
        ##########################################################################
        # Step 1: Create a custom model
        # Change "name" and "description" to suit your own model
        ##########################################################################
        print "\nCreating custom mmodel..."
        data = {"name": name, "base_model_name": base_model, "description": description}
        jsonObject = json.dumps(data).encode('utf-8')
        resp = self.Post(self.endpoint, jsonObject)

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
        uri = self.endpoint + self.custom_id + "/corpora/" + corpus_name
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
        uri = self.endpoint +  self.custom_id + "/corpora/" + self.corpus_name
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
        uri = self.endpoint + self.custom_id + "/words?sort=count"
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
        uri = self.endpoint + self.custom_id + "/words/" + u
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
        uri = self.endpoint + self.custom_id
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
        uri = self.endpoint + self.custom_id + "/words?word_type=user&sort=alphabetical"
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
        uri = self.endpoint + self.custom_id + "/train"
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
        uri = self.endpoint + self.custom_id
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

    def FetchModels(self):
        self.logger.Trace("\nGetting custom models...")
        r = self.Get(self.endpoint)
        return json.loads(r.text)

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
