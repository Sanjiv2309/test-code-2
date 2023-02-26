import psycopg2
import pandas as pd
import numpy  as np
import datetime
from datetime import datetime
from datetime import timedelta
import altair as alt
import streamlit as st

Phone = st.text_input(
        "Enter Phone Number",
        "Phone Number",
       key="placeholder")
# Phone= '9975079843'
# start_date = '2023/02/09'
# end_date = '2023/02/18'

start_date = st.date_input("Start Date", key=1)
end_date = st.date_input("End Date",key=2)

connection = psycopg2.connect(user ="root_user",
            password = "Compounder##167",
            host = "prod-read-replica.c4mnxfuzwfth.ap-south-1.rds.amazonaws.com",
            port = 5432,
            database = "bonatra_db_production")

patient_query=(f"""with table_1 as (
select pa.name,right(pa.mobile,10) as Mobile,approximate_time,
(approximate_time::date) as approximate_date,
value,measurement_unit
from patient  as pa inner join glucose_entry as ge on pa.id=ge.patient_id)
SELECT * FROM table_1 where Mobile = '{Phone}'
and approximate_date >= '{start_date}'and approximate_date <= '{end_date}'""")


cursor = connection.cursor()
cursor.execute(patient_query)
result = cursor.fetchall()
data = pd.read_sql_query(patient_query,connection)


time = []

start = datetime.strptime(start_date, "%Y/%m/%d")
end = datetime.strptime(end_date, "%Y/%m/%d")
end_1 = end + timedelta(1)
date_generated = [start + timedelta(days=x)
                  for x in range(0, (end_1-start).days)]


for date in date_generated:
    time.append(date.strftime('%Y-%m-%d'))

data['new_time'] = [d.time() for d in data['approximate_time']]

name = data['name'].iloc[0]
mobile = data['mobile'].iloc[0]

data['bins'] = data['new_time'].apply(str).str[:2]
data['bins'] = data['bins'].astype(str) + ":00" 

data_1 = data[['approximate_date']].drop_duplicates()
timeDateFormat = data_1["approximate_date"].tolist()


data_2 = data.groupby(['bins', 'approximate_date'])[['value']].mean().round(1)
data_2 = data_2.reset_index()

timeArr = []
for t in timeDateFormat:
    timeArr.append(t.strftime("%Y-%m-%d"))

for i in range(0,len(timeArr)):   
    source = data_2.loc[data_2['approximate_date'] == timeArr[i]]
    base = alt.Chart(source).properties(width=550)
    line = base.mark_line().encode(
    x='bins',
    y='value').properties(
    title= timeArr[i])
    rule_1 = alt.Chart(pd.DataFrame({'y': [40]})).mark_rule(color='red').encode(y='y')
    rule_2 = alt.Chart(pd.DataFrame({'y': [140]})).mark_rule(color='red').encode(y='y')
    print_chart =line+rule_1+rule_2
    st.altair_chart(print_chart)