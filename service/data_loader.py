import csv

from transformers import prune_layer

from model.etf_model import ETFModel, ListOfETFModel


def load_initial_data():
    with open('./etf_security_master.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        list_of_etfs=[]
        for row in reader:
            etfModel = ETFModel(**row)
            list_of_etfs.append(etfModel)
    return ListOfETFModel(list_of_etfs)