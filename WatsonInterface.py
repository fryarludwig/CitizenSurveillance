# -*- coding: utf-8 -*-
from Watson import *
import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

if __name__ == '__main__':
    watson = WatsonUtility(json.load(open('./settings.json', 'r')))

    watson.CreateModel("Test_Scanner_2", "First model to test scanner customization")
    watson.AddCorpusFile()
    watson.ShowOOVs()
    watson.GetModelStatus()
    watson.DeleteModel()
