import pandas as pd
import json
import requests
import datetime

month_map = {
    1: 'jan',
    2: 'feb',
    3: 'mar',
    4: 'apr',
    5: 'may',
    6: 'jun',
    7: 'jul',
    8: 'aug',
    9: 'sep',
    10: 'oct',
    11: 'nov',
    12: 'dec'
}

inverse_month_map = {v: k for k, v in month_map.items()}

previous_years_dates = []
lookback_years = 3
prev_years_month_list = list(range(1, 13))

for i in range(lookback_years, 0, -1):
    previous_year = datetime.date.today().year - i
    previous_years_dates.extend([f'{previous_year}-{month_map[sel_m]}' for sel_m in prev_years_month_list])

current_year = datetime.date.today().year
current_month = datetime.date.today().month
current_year_month_list = list(range(1, current_month + 1))

current_year_adjusted_dates = [f'{current_year}-{month_map[sel_m]}' for sel_m in current_year_month_list]
dates = previous_years_dates + current_year_adjusted_dates

prices = ['value-of-retail-sales-at-current-prices', 'chained-volume-of-retail-sales']
geographies =  ['K03000001']
seasonal_adjustments = ['non-seasonal-adjustment']


df = pd.DataFrame(columns = ['Observation', 'USIC', 'Price', 'Geography', 'SeasonalAdjustment', 'Time'])

for i in range(len(dates)):
    for j in range(len(prices)):
        sel_date = dates[i]
        sel_price = prices[j]

        DATASET_URL = f"https://api.beta.ons.gov.uk/v1/datasets/retail-sales-index-large-and-small-businesses/editions/time-series/versions/33/observations?geography={geographies[0]}&time={sel_date}&unofficialstandardindustrialclassification=*&prices={sel_price}&seasonaladjustment={seasonal_adjustments[0]}"

        response = requests.get(DATASET_URL)
        data = json.loads(response.text)

        observation_list = []
        USIC_list = []
        price_list = []
        geography_list = []
        seasonal_adjustment_list = []
        time_list = []

        if data['observations'] != None:
            for data_point in data['observations']:
                observation_list.append(data_point['observation'])
                USIC_list.append(data_point['dimensions']['UnofficialStandardIndustrialClassification']['id'])
                price_list.append(sel_price)
                geography_list.append(geographies[0])
                seasonal_adjustment_list.append(seasonal_adjustments[0])
                time_list.append(sel_date)

            pre_dict = {
                'Observation': observation_list,
                'USIC': USIC_list,
                'Price': price_list,
                'Geography': geography_list,
                'SeasonalAdjustment': seasonal_adjustment_list,
                'Time': time_list
            }

            df = pd.concat([df, pd.DataFrame(pre_dict)], ignore_index=True)
        else:
            pass

def fix_date(input_date):
    input_date = input_date.split('-')
    input_date_year = input_date[0]
    input_date_month = str(inverse_month_map[input_date[1]])
    return pd.to_datetime(input_date_month + '-' + input_date_year, format='%m-%Y')

df['Time'] = df['Time'].apply(fix_date)
df['Observation'] = df['Observation'].astype(float)
df['USIC'] = df['USIC'].astype(str)
df['Price'] = df['Price'].astype(str)
df['Geography'] = df['Geography'].astype(str)
df['SeasonalAdjustment'] = df['SeasonalAdjustment'].astype(str)
df['USIC_industry'] =  df['USIC'].apply(lambda x: '-'.join(x.split('-')[:-2]))
df['USIC_business'] = df['USIC'].apply(lambda x: '-'.join(x.split('-')[-2:]))
df['Year'] = df['Time'].dt.year

df = df[df['Geography'] == "K03000001"]

avg_rsi = df.groupby(['USIC_industry','USIC_business', 'Price', 'Geography', 'SeasonalAdjustment', 'Year'])['Observation'].mean().reset_index()
avg_rsi['Observation'] = avg_rsi['Observation'].round(2)
avg_rsi['Year'] = avg_rsi['Year'].astype(str)
