# -*- coding: utf-8 -*-
import os
import json
import datetime

from Watson import *


__title__ = 'Watson Training Tool'


WRITE_LOG_FILE = False
SETTINGS_PATH = './settings.json'
CORPUS_PATH = './corpus.txt'
CURRENT_TIME = datetime.datetime.now().strftime('%Y_%m_%d-%H_%M')
LOGFILE_PATH = './Logs/Trainer-{}-log.txt'.format(CURRENT_TIME)

if WRITE_LOG_FILE:
    logger = LogUtility(LOGFILE_PATH)
else:
    logger = LogUtility()

if __name__ == '__main__':
    watson = WatsonUtility(json.load(open(SETTINGS_PATH, 'r')), logger)
    existing_models = watson.FetchModels()
    logger.Info(existing_models)


    # watson.CreateModel("Test_Scanner_2", "First model to test scanner customization")
    # watson.AddCorpusFile()
    # watson.ShowOOVs()
    # watson.GetModelStatus()
    # watson.DeleteModel()
