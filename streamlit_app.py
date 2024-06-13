pip install google-api-python-client
pip install hampel
pip install pandas statsmodels
pip install streamlit

import os
import glob
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from hampel import hampel
from sklearn.metrics import r2_score
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

import os
import json
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

service_account_info = json.loads(os.environ['SERVICE_ACCOUNT'])
scopes = ['https://www.googleapis.com/auth/spreadsheets']
credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=scopes)
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()

google_sheet_url = 'https://docs.google.com/spreadsheets/d/1C9AKwU55jVA_ep3IiQHH6BpoAKQg--yNxcMQ2RLvVYc/edit#gid=1580399618'
spreadsheet_id = google_sheet_url.split('/')[5]


spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
sheets = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
print(sheets)


# get the columns you desire
range_name = 'UK Data (PURO 2024)'
result = sheet.values().get(spreadsheetId=spreadsheet_id,
                        range=range_name).execute()

values = result['values']

# contruct a Pandas DataFrame from the raw values that were returned from the Google Sheet
df = pd.DataFrame(values[0:], columns=values[0])
print(df)

df_clean = df.loc[:,['Job','Site', 'Month End','Spreader Fuel Data','Loader Fuel Data','Task Data / GPS','Rock Spreads','Dropsite Photo (before)','Dropsite Photo (after)','Attestation','Landowner Contract']]
df_clean

# counting the number of 'available', 'missing', 'partially missing', and 'issue' values in the dataframe
counts = df_clean.eq('Done').sum().rename('Available')
counts = counts.to_frame().assign(missing=df_clean.eq('Missing').sum().rename('Missing'),
                                   partially_missing=df_clean.eq('Partially Missing').sum().rename('Partially Missing'),
                                   issue=df_clean.eq('Issue').sum())

print(counts)

# switching the rows and columns in the dataframe
counts_transposed = counts.T

# adding a row with the total number of missing, partially missing, and issue values
counts_transposed['Total'] = counts_transposed.sum(axis=1)
counts_transposed

# removing 'job', 'site', and 'month end' columns
counts_transposed = counts_transposed.drop(['Job', 'Site', 'Month End'], axis=1)
counts_transposed

# Creating Streamlit Dashboard
st.set_page_config(
    page_title="UK Data Integrity (2024)",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

counts_transposed_st = st.dataframe(counts_transposed)

# cols = st.columns([1, 1])

with cols[0]:
    fig = px.pie(counts_transposed, values= 'Total', names=('Available','Missing','Partially Missing','Issue'),
                 title='UK Data Integrity (2024)',
                 height=900, width=600)
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=0),)
    st.plotly_chart(fig, use_container_width=True)

fig.show()
