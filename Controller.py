from requests import get
import pandas as pd
from json import loads

class Controller:
    def __init__(self) -> None:
        self.server = 'http://127.0.0.1:8000'

    def get_indexes(self):
        response = get(self.server + '/indexes')
        if response.status_code != 200:
            return None
        dic = loads(response.text)
        return dic

    def get_historical(self, name, start = None, end = None):
        name = name.replace('&', '%26')
        data = f'name={name}'
        if start != None:
            data += f'&start={start}'
        if end != None:
            data += f'&end={end}'
        response = get(self.server + f'/historical_data?{data}')
        if response.status_code != 200:
            return None
        pf = pd.read_json(response.text).set_index('Date')
        pf.sort_index(inplace=True)
        return pf

    def get_index(self, index: str):
        index = index.replace('&', '%26')
        data = f'name={index}'
        response = get(self.server + f'/index?{data}')
        if response.status_code != 200:
            return None
        dic = loads(response.text)
        pf = pd.DataFrame(dic, index=[0])
        return pf

    def get_index_companies(self, index):
        index = index.replace('&', '%26')
        data = f'name={index}'
        response = get(self.server + f'/index_comapnies?{data}')
        if response.status_code != 200:
            return None
        pf = pd.read_json(response.text).set_index('Date')
        return pf

    def get_company(self, name):
        name = name.replace('&', '%26')
        data = f'name={name}'
        response = get(self.server + f'/company?{data}')
        if response.status_code != 200:
            return None
        dic = loads(response.text)
        pf = pd.DataFrame(dic, index=[0]).set_index('Date')
        return pf