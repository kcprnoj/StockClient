from requests import get
import pandas as pd
from json import loads
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
import math
from sklearn.metrics import mean_squared_error

def windowing_dataset(dataset, step=1):
    dataX, dataY = [], []
    for i in range(len(dataset)-step):
        a= dataset[i:(i+step), 0]
        dataX.append(a)
        dataY.append(dataset[i+step, 0])
    return np.array(dataX), np.array(dataY)

class Controller:
    def __init__(self) -> None:
        self.server = 'http://127.0.0.1:8000'

    def get_indexes(self):
        response = get(self.server + '/indexes')
        if response.status_code != 200:
            return None
        dic = loads(response.text)
        return dic

    def get_historical(self, name, start = None, end = None, interval = None):
        name = name.replace('&', '%26')
        data = f'name={name}'
        if start != None:
            data += f'&start={start}'
        if end != None:
            data += f'&end={end}'
        if interval != None and interval != '1D':
            data += f'&interval={interval}'
        response = get(self.server + f'/historical_data?{data}')
        if response.status_code != 200:
            return None
        pf = pd.read_json(response.text, convert_dates=False)
        pf['Date'] = pd.to_datetime(pf['Date'], format="%d/%m/%Y %H:%M:%S")
        pf = pf.set_index('Date')
        pf.sort_index(inplace=True)
        return pf

    def get_index(self, name: str):
        name = name.replace('&', '%26')
        data = f'name={name}'
        response = get(self.server + f'/index?{data}')
        if response.status_code != 200:
            return None
        dic = loads(response.text)
        pf = pd.DataFrame(dic, index=[0])
        return pf

    def get_index_companies(self, name):
        name = name.replace('&', '%26')
        data = f'name={name}'
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

    def get_prediction(self, name) -> int:
        df = self.get_historical(name, start='01/01/2005')
        if df is None:
            return 0
        print(df)
        closed_data = np.array(df['Close'])
        print(closed_data)
        closed_data = closed_data.reshape(-1,1)
        training_size = int(len(closed_data)*0.65)
        train_data, test_data = closed_data[0:training_size,:], closed_data[training_size:len(closed_data),:1]
        time_step = 100
        x_train, y_train = windowing_dataset(train_data, time_step)
        x_test, y_test = windowing_dataset(test_data, time_step)

        model = LinearRegression()
        model.fit(x_train, y_train)

        predictions = model.predict(x_test)
        print("Przewidziane", predictions[:10][0])
        print("Prawdziwe", y_test[:10][0])

        print("Dokladnosc dla danych treningowych: ", model.score(x_train, y_train))
        print("Dokladnosc dla danych testowych: ", model.score(x_test, y_test))

        train_predict = model.predict(x_train)
        test_predict = model.predict(x_test)
        train_predict = train_predict.reshape(-1, 1)
        test_predict = test_predict.reshape(-1, 1)

        print(f"RMSE train: {math.sqrt(mean_squared_error(y_train, train_predict))}")
        print(f"RMSE test: {math.sqrt(mean_squared_error(y_test, test_predict))}")

        last_values = closed_data[len(closed_data)-100:len(closed_data)]
        last_values = last_values.reshape(1,-1)
        predict = model.predict(last_values).reshape(1,-1)
        return round(predict[0][0], 2)