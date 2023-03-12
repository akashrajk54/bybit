import pip

try:
    import os
    import sys
    import pandas as pd
    from datetime import datetime, timezone
    # To scrap option chain
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from webdriver_manager.chrome import ChromeDriverManager

except Exception as e:
    print(e)
    e = str(e).split(' ')[-1].replace("'", "")
    pip.main(['install', e])

base_dir = os.path.normpath(os.getcwd() + os.sep + os.pardir)
sys.path.insert(1, base_dir)

import bybit
from include import settings

class ByBitManager:
    def __init__(self, expert_name, version, env, symbol, timeframe, limit, start_date, end_date, server):
        self.expert_name = expert_name
        self.version = version
        self.env = env
        self.symbol = symbol
        self.timeframe = timeframe
        self.limit = limit
        self.start_date = start_date
        self.end_date = end_date
        self.server = server
        self.initialize()
        self.summary()


    def summary(self):
        print(
            f'Summary:\n'
            f'ExpertAdvisor name:              {self.expert_name}\n'
            f'ExpertAdvisor version:           {self.version}\n'
            f'ExpertAdvisor environment:       {self.env}\n'
            f'Running on symbol:               {self.symbol}\n'
            f'Timeframe:                       {self.timeframe}\n'
            f'Limit:                           {self.limit}\n'
            f'Start date:                      {self.start_date}\n'
            f'End date:                        {self.end_date}\n'
            f'Server:                          {self.server}\n'
        )

    def initialize(self):
        print()
        print('******')
        environment = self.env
        if environment == 'test':
            print("*** TEST ***")
            self.client = bybit.bybit(test=False, api_key=settings.api_key, api_secret=settings.api_secret)

    def get_ohlc_data(self):

        time_format = '%Y-%m-%d %H:%M:%S'

        # Set the start and end dates for the data range
        start_date_str = self.start_date

        # Convert the start and end dates to Unix timestamps in milliseconds
        start_date = int(datetime.strptime(start_date_str, time_format).replace(tzinfo=timezone.utc).timestamp())

        # Call the kline endpoint with the symbol, interval, and limit parameters
        response = self.client.Kline.Kline_get(symbol=self.symbol, interval=self.timeframe, **{'from':start_date, 'limit':90}).result()

        # Extract the OHLC data from the response
        ohlc_data = response[0]['result']
        data = pd.DataFrame(ohlc_data)

        return data

    def order(self):
        pass

    def is_float(self, num):
        try:
            if float(num) or int(num):
                return True
        except ValueError:
            return False

    def scrap_options_alert(self, symbol_name):
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        path = "https://www.niftytrader.in/nse-option-chain/" + symbol_name.lower()
        driver.get(path)
        driver.implicitly_wait(15)

        big = driver.find_element(By.XPATH, "//div[@class='body border-0']")

        new_str = big.text
        splits = new_str.split()
        driver.quit()

        li = []
        for split in splits:
            split = split.replace(',', '')
            # not float --
            if self.is_float(split) != True:
                # agr '-' hai to directly append
                if split == '-':
                    li.append(split)
                    var = 0
                elif '%' in split:
                    last_num = li.pop()
                    last_num = str(last_num)
                    combine_num = last_num +' '+ split
                    li.append(combine_num)
                    var = 0
                else:
                    if var > 0:
                        last = li.pop()
                        new_str = last + ' ' + split
                        li.append(new_str)
                    if var == 0:
                        li.append(split)
                        var = var + 1

            elif self.is_float(split) == True:
                li.append(split)
                var = 0

        start = 0
        end = 13
        new_list = []
        for i in range (int(len(li)/14)):
            tmp_list = li[start:end]
            new_list.append(tmp_list)
            start = end + 1
            end = end + 14

        df_data = pd.DataFrame(new_list, columns = ['DELTA', 'BUILTUP_CALL', 'OI', 'CHG IN OI', 'IV', 'LTP (CHG %)', 'STRIKE',
                                        'LTP (CHG %)', 'IV', 'CHG IN OI', 'OI', 'BUILTUP_PUT', 'DELTA'])

        return df_data

