
import pip

try:
    import os
    import sys
    import datetime

except Exception as e:
    print(e)
    e = str(e).split(' ').iloc[-1].replace("'", "")
    pip.main(['install', e])

base_dir = os.path.normpath(os.getcwd() + os.sep + os.pardir)
sys.path.insert(1, base_dir)

from include.base.bybit import ByBitManager

manager = ByBitManager(
                    'btcusd_expert',
                    '0.1',
                    'test',
                    'BTCUSD',
                    '15',
                    1000,
                    '2021-01-01 00:00:00',
                    '2023-01-01 00:00:00',
                    'ByBit'
                    )


data = manager.get_ohlc_data()

print('---')

data['open_time'] = [datetime.datetime.fromtimestamp(int(ts), tz=datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S') for ts in data['open_time']]

print(data)

print('---')

sp = manager.scrap_options_alert(symbol_name='NIFTY')
print('sp: ')
print(sp)

