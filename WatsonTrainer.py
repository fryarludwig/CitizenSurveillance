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

    # existing_models = watson.FetchModelsAsList()
    # for model in existing_models:
    #     watson.DeleteModel(model.customization_id)
    #
    # resp = watson.CreateModel("Test_Scanner_2", "First model to test scanner customization")
    # logger.Trace(resp)

    existing_models = watson.FetchModelsAsList()
    logger.Info(existing_models)
    current_corpus = WatsonCorpus("testCorpus", CORPUS_PATH, existing_models[0].customization_id)
    # watson.AddCorpusObject(current_corpus)

    for model in existing_models:
        watson.ShowOOVs(model.customization_id)
        watson.CheckCorpusStatus(model, current_corpus.name)
        watson.StartTraining(model.customization_id)
        # watson.GetModelStatus(model.customization_id)
        results = watson.TranscribeAudio(model.customization_id, "./IS/deer_in_the_road.wav")
        logger.Info(results)