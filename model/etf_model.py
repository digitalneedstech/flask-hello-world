from sqlalchemy.dialects.postgresql import array

import json
class ETFModel:
    def __init__(self, **kwargs):
        self.percentage = 0.0
        self.security_id = kwargs.get('security_id')
        self.symbol = kwargs.get('symbol')
        self.name = kwargs.get('name')
        self.series = kwargs.get('series')

    def updatePercentage(self,percentage):
        self.percentage=percentage

    def to_dict(self):
        return {"percentage":self.percentage,"security_id":self.security_id,"symbol":self.symbol,"name":self.name,"series":self.series}


class ListOfETFModel:
    def __init__(self,etfs:[]):
        self.etfs=etfs

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
