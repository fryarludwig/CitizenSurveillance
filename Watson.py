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

"""
{"words": [
   {
      "display_as": "IEEE",
      "sounds_like": ["I. triple E."],
      "count": 1,
      "source": ["user"],
      "word": "IEEE"
   },
   {
      "display_as": "HHonors",
      "sounds_like": [
         "H. honors",
         "hilton honors"
      ],
      "count": 1,
      "source": ["user"],
      "word": "hhonors"
   },
   {
      "display_as": "TCP/IP",
      "sounds_like": ["T. C. P. I. P."],
      "count": 1,
      "source": ["user"],
      "word": "tcpip"
   }
]}
"""

class WatsonWord:
    def __init__(self, fields=None):
        if fields is None:
            self.display_as  = "TCP/IP"
            self.sounds_like = ["T. C. P. I. P."]
            self.count       = 1
            self.source      = ["user"]
            self.word        = "tcpip"
        else:
            self.__from_json(fields)

    def __from_json(self, fields):
        self.display_as = fields['display_as']
        self.sounds_like = fields['sounds_like']
        self.count = fields['count']
        self.source = fields['source']
        self.word = fields['word']

    def __str__(self):
        return '[{}: {}]'.format(self.word, self.display_as)

    def __repr__(self):
        return '[{}: {}]'.format(repr(self.word), repr(self.display_as))

class WatsonCorpus:
    def __init__(self, corpus_name=None, file_path=None, model_id=None):
        self.name = "" if corpus_name is None else corpus_name
        self.path = "" if file_path is None else file_path
        self.model_id = "" if model_id is None else model_id

class WatsonModel:
    def __init__(self, fields=None):
        if fields is None:
            self.base_model_name = 'en-US_BroadbandModel',
            self.created = ''
            self.customization_id = ''
            self.description = ''
            self.language = ''
            self.name = ''
            self.owner = ''
            self.progress = 0
            self.status = ''
        else:
            self.__from_json(fields)

    def __from_json(self, fields):
        self.base_model_name = fields['base_model_name']
        self.created = fields['created']
        self.customization_id = fields['customization_id']
        self.description = fields['description']
        self.language = fields['language']
        self.name = fields['name']
        self.owner = fields['owner']
        self.progress = fields['progress']
        self.status = fields['status']

    def __str__(self):
        return '{}: {}'.format(self.name, self.customization_id)

class WatsonUtility:
    def __init__(self, settings, logger=None):
        self.headers = settings['headers'] if 'headers' in settings else ""
        self.username = settings['username'] if 'username' in settings else ""
        self.password = settings['password'] if 'password' in settings else ""
        self.base_url = settings['base_url'] if 'base_url' in settings else ""
        self.endpoint = settings['endpoint'] if 'endpoint' in settings else ""
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
        return 'User: {}\nPass: {}\nUrl:  {}\nAPI:  {}'.format(
            self.username, self.password, self.base_url, self.endpoint)

    def Post(self, destination, payload=None, verify=False, header=None):
        self.logger.Trace("Posting: {}".format(destination))
        http_header = self.headers if header is None else header
        resp = requests.post(destination, auth=(self.username, self.password), verify=verify,
                             headers=http_header, data=payload)
        self.logger.Trace("Response: {}".format(resp))
        return resp

    def Put(self, destination, payload=None, verify=False):
        self.logger.Trace("Putting: {}".format(destination))
        resp = requests.put(destination, auth=(self.username, self.password), verify=verify,
                             headers=self.headers, data=payload)
        self.logger.Trace("Response: {}".format(resp))
        return resp

    def Get(self, destination, verify=False):
        self.logger.Trace("Getting: {}".format(destination))
        resp = requests.get(destination, auth=(self.username, self.password), verify=verify, headers=self.headers)
        self.logger.Trace("Response: {}".format(resp))
        return resp

    def Delete(self, destination, verify=False):
        self.logger.Trace("Deleting: {}".format(destination))
        resp = requests.delete(destination, auth=(self.username, self.password), verify=verify, headers=self.headers)
        self.logger.Trace("Response: {}".format(resp))
        return resp

    def CreateModel(self, name, description, base_model="en-US_BroadbandModel"):
        ##########################################################################
        # Step 1: Create a custom model
        # Change "name" and "description" to suit your own model
        ##########################################################################
        self.logger.Trace("Creating custom mmodel...")
        data = {"name": name, "base_model_name": base_model, "description": description}
        jsonObject = json.dumps(data).encode('utf-8')
        resp = self.Post(self.endpoint, jsonObject)

        if resp.status_code != 201:
            self.logger.Error("Failed to create model" + r.text)

        respJson = resp.json()
        if 'customization_id' in respJson:
            return respJson['customization_id']
        else:
            return None

    def AddCorpusFile(self, model_id, corpus_file, corpus_name):
        """

        :type model: WatsonModel
        :type corpus_file: str
        :type corpus_name: str
        """
        self.logger.Trace("Adding corpus file...")
        uri = self.endpoint + model_id + "/corpora/" + corpus_name
        with open(corpus_file, 'rb') as f:
            r = self.Post(uri, f)
        if r.status_code != 201:
            self.logger.Error("Failed to add corpus file" + r.text)
        return r

    def AddCorpusObject(self, corpus):
        """
        :type corpus: WatsonCorpus
        """
        return self.AddCorpusFile(corpus.model_id, corpus.path, corpus.name)


    def CheckCorpusStatus(self, model, corpus_name):
        ##########################################################################
        # Step 3: Get status of corpus file just added.
        # After corpus is uploaded, there is some analysis done to extract OOVs.
        # One cannot upload a new corpus or words while this analysis is on-going so
        # we need to loop until the status becomes 'analyzed' for this corpus.
        ##########################################################################
        """

        :type model: WatsonModel
        """
        self.logger.Trace("Checking status of corpus analysis...")
        r = self.Get(self.endpoint +  model.customization_id + "/corpora/" + corpus_name)
        if r.status_code == 200 or r.status_code == 201:
            status = r.json()['status']
            time_to_run = 10
            while (status != 'analyzed'):
                time.sleep(10)
                r = self.Get(self.endpoint +  model.customization_id + "/corpora/" + corpus_name)
                status = r.json()['status']
                self.logger.Info("status: {} ({})".format(status, time_to_run))
                time_to_run += 10
            print "Corpus analysis done!"
        else:
            self.logger.Error("Received an error response while adding corpus: {}".format(r.text))

    def ShowOOVs(self, custom_id):
        self.logger.Trace("Showing OOVs...")
        uri = self.endpoint + custom_id + "/words?sort=count"
        r = self.Get(uri)
        self.logger.Info("Listing words returns: " + r.text)
        file = codecs.open("output.OOVs.corpus", 'wb', 'utf-8')
        file.write(r.text)

    def AddWord(self, custom_id):
        ##########################################################################
        # Step 4: Add a single user word
        # One can pass sounds_like and display_as fields or leave empty (if empty
        # the service will try to create its own version of sounds_like)
        ##########################################################################
        self.logger.Trace("Adding single word...")
        data = {"sounds_like": ["T. C. P. I. P."], "display_as": "TCP/IP"}
        wordToAdd = "tcpip"
        u = unicode(wordToAdd, "utf-8")
        uri = self.endpoint + custom_id + "/words/" + u
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

    def GetModelStatus(self, custom_id):
        ##########################################################################
        # Get status of model - only continue to training if 'ready'
        ##########################################################################
        uri = self.endpoint + custom_id
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
            self.logger.Info("status: {} ({})".format(status, time_to_run))
            time_to_run += 10

        print "\nListing words..."
        uri = self.endpoint + custom_id + "/words?word_type=user&sort=alphabetical"
        r = self.Get(uri)
        file = codecs.open("output.OOVs.user", 'wb', 'utf-8')
        print r.text
        file.write(r.text)
        print "Words list from user-added words saved in file: output.OOVs.user"

    def StartTraining(self, model_id):
        self.logger.Trace("Training custom model...")
        uri = self.endpoint + model_id + "/train"
        jsonObject = json.dumps({}).encode('utf-8')
        r = self.Post(uri, jsonObject)
        if r.status_code != 200:
            print "Training failed to start - exiting!"

    def UpdateTrainingStatus(self):
        ##########################################################################
        # Get status of training and loop until done
        ##########################################################################
        r = self.Get(self.endpoint + self.custom_id)
        status = r.json()['status']
        time_to_run = 10
        while (status != 'available'):
            time.sleep(10)
            r = self.Get(self.endpoint + self.custom_id)
            status = r.json()['status']
            self.logger.Info("status: {} ({})".format(status, time_to_run))
            time_to_run += 10
        print "Training complete!"

    def TranscribeAudio(self, model_id, file_path):
        """

        :param model_id:
        :param file_path:
        :return:
        """
        self.logger.Trace("Attempting to transcribe audio file...")
        uri = self.base_url + 'v1/recognize'
        headers = {"Content-Type": "audio/wav", "customization_id": model_id}
        with open(file_path, 'rb') as f:
            r = self.Post(uri, payload=f, header=headers)
        if r.status_code != 200:
            self.logger.Error("Failed to transcibe audio file [{}] {}".format(
                os.path.basename(file_path), r.text))
        else:
            counter = 0
            out_path = "./Results/transcribe_result_{}.json"
            while os.path.exists(out_path.format(counter)):
                counter += 1
            file = codecs.open(out_path.format(counter), 'wb', 'utf-8')
            file.write(r.text)
            return json.loads(r.text)


    def FetchModelsAsList(self):
        """

        :rtype: list of WatsonModel
        """
        r = self.Get(self.endpoint)
        models = json.loads(r.text)
        results = []
        if 'customizations' in models:
            for model in models['customizations']:
                results.append(WatsonModel(model))
        return results


    def FetchModelsAsDict(self):
        """

        :rtype: dict of (str, WatsonModel)
        """
        r = self.Get(self.endpoint)
        models = json.loads(r.text)
        results = {}
        if 'customizations' in models:
            for jsonItem in models['customizations']:
                model = WatsonModel(jsonItem)
                results[model.customization_id] = model

        return results

    def DeleteModel(self, model_id):
        """

        :type model_id: str
        """
        self.logger.Warn("Deleting custom model...")
        r = self.Delete(self.endpoint + model_id)
