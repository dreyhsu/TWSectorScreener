from finlab.data import Data
import talib
import pandas as pd

data = Data()

rev = data.get("當月營收")
close = data.get("收盤價")
vol = data.get('成交金額')
low = data.get('最低價')
high = data.get('最高價')
compare_rev = data.get("上月比較增減(%)")
fh_rate = pd.read_csv("C:/Users/Drey/finlab_ml_course/history/items/forign_hold_ratio/fs_df.csv").set_index('date')
fh_rate.index = pd.to_datetime(fh_rate.index)
# rev.index = rev.index.shift(5, "d")

def bias(n):
    return close / close.rolling(n, min_periods=1).mean()

def acc(n):
    return close.shift(n) / (close.shift(2*n) + close) * 2

def acc_fs(n):
    return fh_rate.shift(n) / (fh_rate.shift(2*n) + fh_rate) * 2

def rsv(n):
    l = close.rolling(n, min_periods=1).min()
    h = close.rolling(n, min_periods=1).max()
    
    return (close - l) / (h - l)

def mom(n):
    return (rev / rev.shift(1)).shift(n)

# 月營收平均
def return_MA(n):
    return rev.rolling(window=2).mean()

def roe_pb():
    return roe_pb_df

def vol_MA(n):
    return vol.rolling(window=n).mean()

features = {
    'mom1': mom(1),
    'mom2': mom(2),
    'mom3': mom(3),
    'mom4': mom(4),
    'mom5': mom(5),
    'mom6': mom(6),
    'mom7': mom(7),
    'mom8': mom(8),
    'mom9': mom(9),
    
    'bias5': bias(5),
    'bias10': bias(10),
    'bias20': bias(20),
    'bias60': bias(60),
    'bias120': bias(120),
    'bias240': bias(240),
    
    'acc5': acc(5),
    'acc10': acc(10),
    'acc20': acc(20),
    'acc60': acc(60),
    'acc120': acc(120),
    'acc240': acc(240),

    'acc_fs5': acc_fs(5),
    'acc_fs10': acc_fs(10),
    'acc_fs20': acc_fs(20),
    'acc_fs60': acc_fs(60),
    'acc_fs120': acc_fs(120),
    'acc_fs240': acc_fs(240),

    'rsv5': rsv(5),
    'rsv10': rsv(10),
    'rsv20': rsv(20),
    'rsv60': rsv(60),
    'rsv120': rsv(120),
    'rsv240': rsv(240),

    'return_MA2': return_MA(2),
    'return_MA5': return_MA(5),
    'return_MA10': return_MA(10),
    
    'vol_MA2': vol_MA(2),
    'vol_MA5': vol_MA(5),
    'vol_MA10': vol_MA(10),

    # 'roe_pb' : roe_pb(),
}

every_month = rev.index

# features['bias20'].reindex(every_month, method='ffill')

for name, f in features.items():
    features[name] = f.reindex(every_month, method='ffill')

for name, f in features.items():
    features[name] = f.unstack()

dataset = pd.DataFrame(features)
feature_names = list(dataset.columns)
dataset.index = dataset.index.set_names('date', level=1)

from finlab import ml

ml.add_profit_prediction(dataset)
ml.add_rank_prediction(dataset)

print(dataset.shape)

def drop_extreme_case(dataset, feature_names, thresh=0.01):
    
    extreme_cases = pd.Series(False, index=dataset.index)
    for f in feature_names:
        tf = dataset[f]
        extreme_cases = extreme_cases | (tf < tf.quantile(thresh)) | (tf > tf.quantile(1-thresh))
    dataset = dataset[~extreme_cases]
    return dataset

dataset_drop_extreme_case = drop_extreme_case(dataset,feature_names, thresh=0.01)

print(dataset_drop_extreme_case.shape)

dataset_dropna = dataset_drop_extreme_case.dropna(how='any')
dataset_dropna = dataset_dropna.reset_index().set_index("date")

dataset_drop_extreme_case.index.get_level_values("date")

from sklearn.preprocessing import MinMaxScaler

scaler =  MinMaxScaler(feature_range=(0, 1)).fit(dataset_dropna[feature_names])
dataset_dropna[feature_names] = scaler.transform(dataset_dropna[feature_names])

dataset_train = dataset_dropna.loc[:'2017']
dataset_test = dataset_dropna.loc['2018':]

import keras
from keras.initializers import he_normal
import os

os.environ['KMP_DUPLICATE_LIB_OK']='True'

model = keras.models.Sequential()
model.add(keras.layers.Dense(100, activation='relu',
                      input_shape=(len(feature_names),),
                      kernel_initializer=he_normal(seed=0)))
model.add(keras.layers.Dense(100, activation='relu',
                      kernel_initializer=he_normal(seed=0)))
model.add(keras.layers.Dropout(0.7))
model.add(keras.layers.Dense(1, activation='sigmoid'))


model.summary()

model.compile(loss='mean_squared_error',
              optimizer="adam",)

print('start fitting')
history = model.fit(dataset_train[feature_names], dataset_train['rank'],
                    batch_size=1000,
                    epochs=225,
                    verbose=1,
                    validation_split=0.1, )

import matplotlib.pyplot as plt
plt.plot(history.history['val_loss'][1:])
plt.plot(history.history['loss'][1:])

import lightgbm as lgb
cf = lgb.LGBMRegressor(n_estimators=500)
cf.fit(dataset_train[feature_names].astype(float), dataset_train['rank'])

from sklearn.ensemble import RandomForestRegressor

cf2 = RandomForestRegressor(n_estimators=100)
cf2.fit(dataset_train[feature_names].astype(float), dataset_train['rank'])

feature_imp = pd.DataFrame(zip(cf.feature_importances_, feature_names), 
                           columns=['Value','Feature']).sort_values('Value', ascending=False)
feature_imp
import seaborn as sns
sns.barplot(x="Value", y="Feature", data=feature_imp)

import numpy as np
dataset_drop = dataset.dropna(subset=feature_names+['return'])
# Option 1: Drop rows with NaN or infinity
dataset_drop = dataset_drop.replace([np.inf, -np.inf], np.nan).dropna(subset=feature_names)

# Option 2: Fill NaN with a specific value (e.g., mean, median, or zero)
dataset_drop = dataset_drop.fillna(dataset_drop.mean())

vals = model.predict(dataset_drop[feature_names].astype(float))
dataset_drop['result1'] = pd.Series(vals.swapaxes(0,1)[0], dataset_drop.index)

vals = cf.predict(dataset_drop[feature_names].astype(float))
dataset_drop['result2'] = pd.Series(vals, dataset_drop.index)

vals = cf2.predict(dataset_drop[feature_names].astype(float))
dataset_drop['result3'] = pd.Series(vals, dataset_drop.index)

dataset_drop = dataset_drop.reset_index().set_index("date")

import math


dates = sorted(list(set(dataset_drop.index)))

rs = []
for d in dates:
    
    dataset_time = dataset_drop.loc[d]
    
    dataset_time = drop_extreme_case(dataset_time, 
        feature_names, thresh=0.01)
    
    rank = dataset_time['result1'] + dataset_time['result2'] + dataset_time['result3'] 
    
    condition = (rank >= rank.nlargest(5).iloc[-1]) 
    r = dataset_time['return'][condition].mean()

    rs.append(r * (1-3/1000-1.425/1000*2*0.6))

rs = pd.Series(rs, index=dates)['2016':].cumprod()

s0050 = close['0050']['2016':]

pd.DataFrame({'nn strategy return':rs.reindex(s0050.index, method='ffill'), '0050 return':s0050/s0050[0]}).plot()

dataset.index.levels[1]

# get the latest dataset
last_date = "2021-12-15"#dataset.index.levels[1].max()
is_last_date = dataset.index.get_level_values('date') == last_date
last_dataset = dataset[is_last_date].copy()


last_dataset = drop_extreme_case(last_dataset, 
    ['bias60', 'bias120', 'bias240', 'mom1', 'mom2', 'mom3', 'mom4', 'mom5', 'mom6'], thresh=0.01)


# remove NaN testcases
last_dataset = last_dataset.dropna(subset=feature_names)

# predict

vals = model.predict(last_dataset[feature_names].astype(float))
last_dataset['result1'] = pd.Series(vals.swapaxes(0,1)[0], last_dataset.index)

vals = cf.predict(last_dataset[feature_names].astype(float))
last_dataset['result2'] = pd.Series(vals, last_dataset.index)

vals = cf2.predict(last_dataset[feature_names].astype(float))
last_dataset['result3'] = pd.Series(vals, last_dataset.index)

# calculate score

rank = last_dataset['result1'] + last_dataset['result2'] + last_dataset['result3']
condition = (rank >= rank.nlargest(20).iloc[-1]) 

# plot rank distribution
rank.hist(bins=20)


# show the best 20 stocks
slist1 = rank[condition].reset_index()['stock_id']
