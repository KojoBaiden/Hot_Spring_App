import streamlit as st
import pandas as pd
import requests
import bs4 
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
count = 0

st.set_page_config(layout="wide")
st.image("powergen.JPG",width=1750)
st.markdown("<h1 style='text-align: center; color: black;'>MISO FORECASTING TOOL - HOT SPRING (THE WUESTE WONDER TOOL)</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: black;'>Max MW Capability Based on Forecast Hourly Ambient Temperatures</h1>", unsafe_allow_html=True)

st.markdown("---")

m = []
o = []
s = []

DF_Max_2X1 = 620
DF_Min_2X1 = 450
DF_Max_1X1 = 310
DF_Min_1X1 = 210
DF_MW_bias_2X1 = 0
DF_MW_bias_1X1 = 0

    
url = "https://forecast.weather.gov/MapClick.php?lat=34.36&lon=-92.82&lg=english&&FcstType=digitalDWML"
page = requests.get(url)
soup = BeautifulSoup(page.content,features="html.parser")
        
for i in soup.find_all('time-layout'):
    for j in i.find_all('start-valid-time'):
        for a in j:
            m.append(a.text)
                                
for i in soup.find_all('parameters'):
    for j in i.find_all('temperature',{'type':'hourly'}):
        for a in j:
            o.append(a.text)
                                
for i in soup.find_all('parameters'):
    for j in i.find_all('humidity',{'type':'relative', 'units':'percent'}):
        for a in j:
            s.append(a.text)
                    
weather_data = pd.DataFrame({'Date_time': pd.to_datetime(m),
                             'Temp' : o,
                             'Humidity' : s})
    
weather_data['Hour'] = weather_data['Date_time'].dt.hour 
weather_data['Date'] = weather_data['Date_time'].dt.date
weather_data['Temp'] = np.where(weather_data['Temp']=='',0, weather_data['Temp'])
weather_data['Temp'] = weather_data['Temp'].astype(int)
weather_data['Humidity'] = weather_data['Humidity'].astype(int)
weather_data["Inlet Temp"] =np.where(weather_data['Temp'] > 70, 0.7405*weather_data['Temp']-0.0000000000004, weather_data['Temp'])
del(weather_data['Date_time'])
weather_data = weather_data.loc[:,['Date','Hour','Temp','Inlet Temp','Humidity']]

c1,c2 = st.columns(2)
with c1:
    select_date = st.selectbox("Forecast Date", options=weather_data['Date'].unique(), key="1")
with c2:
    select_hour = st.selectbox("Forecast Hour", options=weather_data['Hour'].unique(), key="2")

st.markdown("---")    
#select_date = st.selectbox("Forecast Date", options=weather_data['Date'].unique())
#select_hour = st.selectbox("Forecast Hour", options=weather_data['Hour'].unique())
weather_data = weather_data[(weather_data['Date'] == select_date) & (weather_data['Hour'] >= select_hour)]

#2X1 Chiller In and Duct Off
weather_data['ch_in_d_off_2'] = round(-0.459*weather_data['Inlet Temp'] - 0.029762*weather_data['Humidity']-0.006851*weather_data['Inlet Temp']**2 + 0.0004+547.848118 + DF_MW_bias_2X1,2)
#2X1 Chiller In and Duct In
weather_data['ch_in_d_on_2'] = round(-1.755*weather_data['Inlet Temp']  -0.012612*weather_data['Humidity'] +0.0033197*weather_data['Inlet Temp']**2 + 0.00877+695.464415 + DF_MW_bias_2X1,2)
#2X1 Chiller Out and Duct Off
weather_data['ch_out_d_off_2'] = round(-0.459*weather_data['Temp'] - 0.029762*weather_data['Humidity']-0.006851*weather_data['Temp']**2 -0.0004+547.848118 + DF_MW_bias_2X1,2)
#2X1 Chiller Out and Duct In
weather_data['ch_out_d_on_2'] = round(-1.755*weather_data['Temp'] -0.012612*weather_data['Humidity'] +0.0033197*weather_data['Temp']**2 + 0.00877+695.464415 + DF_MW_bias_2X1,2)
#1X1 Chiller In and Duct Off
weather_data['ch_in_d_off_1'] = round(2.67103*weather_data['Inlet Temp'] + 0.00182226*weather_data['Humidity']-0.031426775*weather_data['Inlet Temp']**2 + 0+189.93371 + DF_MW_bias_1X1,2)
#1X1 Chiller In and Duct In
weather_data['ch_in_d_on_1'] = round(1.76294*weather_data['Inlet Temp'] -0.16230757*weather_data['Humidity'] -0.022717337*weather_data['Inlet Temp']**2 + 0+283.536005 + DF_MW_bias_1X1,2)
#1X1 Chiller Out and Duct Off  
weather_data['ch_out_d_off_1'] = round(2.67103*weather_data['Temp'] + 0.00182226*weather_data['Humidity']-0.031426775*weather_data['Temp']**2 + 0+189.93371 + DF_MW_bias_1X1,2)
#1X1 Chiller Out and Duct In
weather_data['ch_out_d_on_1'] = round(1.76294*weather_data['Temp'] -0.16230757*weather_data['Humidity'] -0.022717337*weather_data['Temp']**2 + 0+283.536005 + DF_MW_bias_1X1,2)

weather_data.to_csv('weather_data.csv')

st.markdown("<h2 style='text-align: center; color: black;'>Hot Spring 2X1 FORECAST TABLE & DF</h1>", unsafe_allow_html=True)

#st.subheader("Hot Spring 2X1 FORECAST TABLE & DF")

data_1 = weather_data
select_evap = st.radio(" Air Cooling Status", options=("IN","OUT"), key="3")
#count += 1

hour_reg = st.radio("Do you want to enter any biases?", options = ("NO", "YES"), key="4")

if hour_reg == "YES":
    st.write("Please enter hour(s) and Reg/Max MW value(s)")
    col0, col1, col2, col3, col4, col5, col6, col7, col8, col9= st.columns(10)
    with col0:      
        Hour = st.selectbox("Hour", options=data_1['Hour'].unique(), key="5")
    with col1:
        REG = st.text_input("Hourly REG", key = "12",value=0)
    
    with col2:
        Max = st.text_input("Hourly Max", key="13", value=0)

    if "mdf" not in st.session_state:
        st.session_state.mdf = pd.DataFrame(columns=['Hour', 'Hourly REG', 'Hourly Max'])

    run = st.button('Submit',key ="10")
    if run:
        df_new = pd.DataFrame([{'Hour':Hour, 
                                'Hourly REG': REG,
                                'Hourly Max' : Max}])
        df_new["Hourly REG"] = df_new["Hourly REG"].astype(int)
        df_new["Hourly Max"] = df_new["Hourly Max"].astype(int)
        df_new = df_new.drop_duplicates(subset=['Hour'], keep='last')
        #st.dataframe(df_new)
        st.session_state.mdf = pd.concat([st.session_state.mdf,df_new], axis=0).drop_duplicates(subset=['Hour'], keep='last') #working here-----
        st.dataframe(st.session_state.mdf)
    data_1 = data_1.merge(st.session_state.mdf, on = 'Hour', how = 'left')
    data_1['REG Max'] = np.where(select_evap=="IN", data_1['ch_in_d_off_2'], 
                             np.where(select_evap=="OUT",data_1['ch_out_d_off_2'],0))
    data_1 = data_1.assign(a = np.where(select_evap=="IN",data_1['ch_in_d_on_2'], 
                                    np.where(select_evap=="OUT",data_1['ch_out_d_on_2'],0)))
    data_1 = data_1.assign(b = np.where(data_1['a'] < DF_Max_2X1, data_1['a'],DF_Max_2X1))
    data_1 = data_1.assign(Max_Net_Gen = np.where(data_1['b'] > DF_Min_2X1, data_1['b'],DF_Min_2X1))
    data_1 = data_1.fillna(0)
    data_1['REG_to_PCI'] = data_1['REG Max'] + data_1['Hourly REG']
    data_1['Max_Net_PCI'] = data_1['Max_Net_Gen']+data_1['Hourly Max']
    data_1 = data_1.loc[:,['Hour','Temp', 'Humidity','REG Max','Hourly REG','REG_to_PCI','Max_Net_Gen','Hourly Max','Max_Net_PCI']]
    data_1 = data_1.rename(columns = {'Hour':'Hour Ending', 'Temp':'Ambient Temp (°F)','REG Max':'REG Max Generation Available (MW)','Hourly REG':'Hourly REG Max MW Bias','REG_to_PCI':
        'Max Net Generation Available','Hourly Max':'Hourly Max Net MW Bias','Max_Net_PCI':'Submitted for Export to PCI'})
    data_1 = data_1.round(decimals=0)
    data_1['Hourly REG Max MW Bias'] = data_1['Hourly REG Max MW Bias'].replace(0,"") #CHANGED HERE------------
    data_1['Hourly Max Net MW Bias'] = data_1['Hourly Max Net MW Bias'].replace(0,"")
    data_1.to_csv('data_1.csv') 
    v1,v2 = st.columns(2)
    with v1:
        gd = GridOptionsBuilder.from_dataframe(data_1)
        gd.configure_pagination(enabled=True)
        gd.configure_side_bar()
        gd.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=False)
        gridoptions = gd.build()
        grid_table = AgGrid(data_1, gridOptions=gridoptions,
                            update_mode=GridUpdateMode.SELECTION_CHANGED,
                            allow_unsafe_jscode=True,
                            theme='balham',
                            fit_columns_on_grid_load=True)
    v1.download_button(label="Download CSV", data = data_1.to_csv(),  mime="text/csv")
    with v2:
        fig = make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(go.Scatter(x=data_1['Hour Ending'], y=data_1['REG Max Generation Available (MW)'], name = "REG Max Generation Available (MW)"),
                     secondary_y= False)
        fig.add_trace(go.Scatter(x=data_1['Hour Ending'], y=data_1['Ambient Temp (°F)'], name = "Ambient Temp"),
                    secondary_y=True)
        fig.add_trace(go.Scatter(x=data_1['Hour Ending'], y=data_1['Submitted for Export to PCI'], name = "Submitted for Export to PCI"),
                    secondary_y=False)
        fig.update_layout(title_text = "<b>2X1 Capability Based on Forecasted Ambient Temp & Humidity</b>",
                    title_x = 0.5,xaxis_range = ["0","23"])
        fig.update_xaxes(title_text='Hour Ending', minor_ticks = 'inside')
        fig.update_yaxes(title_text = 'Output (MW)',minor_ticks = 'inside', secondary_y=False)
        fig.update_yaxes(title_text = 'Ambient Temp (°F)',minor_ticks = 'inside', secondary_y=True)
        fig.update_layout(legend = dict(orientation = "h",
                                x=0,
                                y=1.15,
                                title_font_family="Sitka Small",
                                bgcolor="LightBlue",
                                bordercolor="Black",
                                borderwidth=2))
    v2.write(fig)


else:
    data_1 = weather_data
    data_1['Hourly REG'] = 0
    data_1['Hourly Max'] = 0
    data_1['REG Max'] = np.where(select_evap=="IN", data_1['ch_in_d_off_2'], 
                             np.where(select_evap=="OUT",data_1['ch_out_d_off_2'],0))

    #data_1['Hourly REG'] = 0
    data_1['REG_to_PCI'] = data_1['REG Max'] + data_1['Hourly REG'] 
    data_1 = data_1.assign(a = np.where(select_evap=="IN",data_1['ch_in_d_on_2'], 
                                    np.where(select_evap=="OUT",data_1['ch_out_d_on_2'],0)))
                       
    data_1 = data_1.assign(b = np.where(data_1['a'] < DF_Max_2X1, data_1['a'],DF_Max_2X1))
    data_1 = data_1.assign(Max_Net_Gen = np.where(data_1['b'] > DF_Min_2X1, data_1['b'],DF_Min_2X1))
    data_1['Max_Net_PCI'] = data_1['Max_Net_Gen'] + data_1['Hourly Max']
    data_1 = data_1.loc[:,['Hour','Temp', 'Humidity','REG Max','Hourly REG','REG_to_PCI','Max_Net_Gen','Hourly Max','Max_Net_PCI']]
    data_1 = data_1.rename(columns = {'Hour':'Hour Ending', 'Temp':'Ambient Temp (°F)','REG Max':'REG Max Generation Available (MW)','Hourly REG':'Hourly REG Max MW Bias','REG_to_PCI':
    'Max Net Generation Available','Hourly Max':'Hourly Max Net MW Bias','Max_Net_PCI':'Submitted for Export to PCI'})
    data_1 = data_1.round(decimals=0)
    data_1['Hourly REG Max MW Bias'] = data_1['Hourly REG Max MW Bias'].replace(0,"") #CHANGED HERE------------
    data_1['Hourly Max Net MW Bias'] = data_1['Hourly Max Net MW Bias'].replace(0,"")
    data_1.to_csv('data_1.csv')

    v1,v2 = st.columns(2)
    with v1:
        gd = GridOptionsBuilder.from_dataframe(data_1)
        gd.configure_pagination(enabled=True)
        gd.configure_side_bar()
        gd.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=False)
        gridoptions = gd.build()
        grid_table = AgGrid(data_1, gridOptions=gridoptions,
                            update_mode=GridUpdateMode.SELECTION_CHANGED,
                            allow_unsafe_jscode=True,
                            theme='balham',
                            fit_columns_on_grid_load=True)
    v1.download_button(label="Download CSV", data = data_1.to_csv(),  mime="text/csv")
    with v2:
        fig = make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(go.Scatter(x=data_1['Hour Ending'], y=data_1['REG Max Generation Available (MW)'], name = "REG Max Generation Available (MW)"),
                     secondary_y= False)
        fig.add_trace(go.Scatter(x=data_1['Hour Ending'], y=data_1['Ambient Temp (°F)'], name = "Ambient Temp"),
                    secondary_y=True)
        fig.add_trace(go.Scatter(x=data_1['Hour Ending'], y=data_1['Submitted for Export to PCI'], name = "Submitted for Export to PCI"),
                    secondary_y=False)
        fig.update_layout(title_text = "<b>2X1 Capability Based on Forecasted Ambient Temp & Humidity</b>",
                    title_x = 0.5,xaxis_range = ["0","23"])
        fig.update_xaxes(title_text='Hour Ending', minor_ticks = 'inside')
        fig.update_yaxes(title_text = 'Output (MW)',minor_ticks = 'inside', secondary_y=False)
        fig.update_yaxes(title_text = 'Ambient Temp (°F)',minor_ticks = 'inside', secondary_y=True)
        fig.update_layout(legend = dict(orientation = "h",
                                x=0,
                                y=1.15,
                                title_font_family="Sitka Small",
                                bgcolor="LightBlue",
                                bordercolor="Black",
                                borderwidth=2))
        v2.write(fig)
st.markdown("---")

st.markdown("<h2 style='text-align: center; color: black;'>Hot Spring 1X1 FORECAST TABLE & DF</h1>", unsafe_allow_html=True)
#count = 3
#st.subheader("Hot Spring 1X1 FORECAST TABLE & DF")
data_2 = pd.read_csv('weather_data.csv')
select_evap = st.radio(" Air Cooling Status", options=("IN","OUT"), key="6")
#count += 1

hour_reg = st.radio("Do you want to enter any biases?", options = ("NO", "YES"), key="7")
if hour_reg == "YES":
    st.write("Please enter hour(s) and Reg/Max MW value(s)")
    col0, col1, col2, col3, col4, col5, col6, col7, col8, col9= st.columns(10)
    with col0:      
        Hour = st.selectbox("Hour", options=data_2['Hour'].unique(), key="8")
    with col1:
        REG = st.text_input("Hourly REG", value = 0)
    
    with col2:
        Max = st.text_input("Hourly Max", value = 0)

    if "ndf" not in st.session_state:
        st.session_state.ndf = pd.DataFrame(columns=['Hour', 'Hourly REG', 'Hourly Max'])


    run = st.button('Submit', key ="11")
    if run:
        df_new_1 = pd.DataFrame([{'Hour':Hour, 
                                'Hourly REG': REG,
                                'Hourly Max' : Max}])
        df_new_1["Hourly REG"] = df_new_1["Hourly REG"].astype(int)
        df_new_1["Hourly Max"] = df_new_1["Hourly Max"].astype(int)
        df_new_1 = df_new_1.drop_duplicates(subset=['Hour'], keep='last')
        #st.dataframe(df_new)
        st.session_state.ndf = pd.concat([st.session_state.ndf,df_new_1], axis=0).drop_duplicates(subset=['Hour'], keep='last')
        st.dataframe(st.session_state.ndf)
    data_2 = data_2.merge(st.session_state.ndf, on = 'Hour', how = 'left')
    data_2['REG Max']  = np.where(select_evap=="IN", data_2['ch_in_d_off_1'], data_2['ch_out_d_off_1'])
    data_2 = data_2.assign(a = np.where(select_evap=='IN',data_2['ch_in_d_on_1'], data_2['ch_out_d_on_1']))
    data_2 = data_2.assign(b = np.where(data_2['a'] < DF_Max_1X1, data_2['a'],DF_Max_1X1))
    data_2 = data_2.assign(Max_Net_Gen = np.where(data_2['b'] > DF_Min_1X1, data_2['b'],DF_Min_1X1))                         
    data_2 = data_2.fillna(0)
    data_2['REG_to_PCI'] = data_2['REG Max'] + data_2['Hourly REG']
    data_2['Max_Net_PCI'] = data_2['Max_Net_Gen']+data_2['Hourly Max']
    data_2 = data_2.loc[:,['Hour','Temp', 'Humidity','REG Max','Hourly REG','REG_to_PCI','Max_Net_Gen','Hourly Max','Max_Net_PCI']]
    data_2 = data_2.rename(columns = {'Hour':'Hour Ending', 'Temp':'Ambient Temp (°F)','REG Max':'REG Max Generation Available (MW)','Hourly REG':'Hourly REG Max MW Bias','REG_to_PCI':
    'Max Net Generation Available','Hourly Max':'Hourly Max Net MW Bias','Max_Net_PCI':'Submitted for Export to PCI'})
    data_2 = data_2.round(decimals=0)
    data_2['Hourly REG Max MW Bias'] = data_2['Hourly REG Max MW Bias'].replace(0,"") #CHANGED HERE------------
    data_2['Hourly Max Net MW Bias'] = data_2['Hourly Max Net MW Bias'].replace(0,"")
    data_2.to_csv('data_2.csv')

    v1,v2 = st.columns(2)
    
    with v1:
        gd = GridOptionsBuilder.from_dataframe(data_2)
        gd.configure_pagination(enabled=True)
        gd.configure_side_bar()
        gd.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=False)
        gridoptions = gd.build()
        grid_table = AgGrid(data_2, gridOptions=gridoptions,
                            update_mode=GridUpdateMode.SELECTION_CHANGED,
                            allow_unsafe_jscode=True,
                            theme='balham',
                            fit_columns_on_grid_load=True)
    v1.download_button(label="Download CSV", data = data_2.to_csv(),  mime="text/csv")
    with v2:
        fig = make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(go.Scatter(x=data_2['Hour Ending'], y=data_2['REG Max Generation Available (MW)'], name = "REG Max Generation Available (MW)"),
                     secondary_y= False)
        fig.add_trace(go.Scatter(x=data_2['Hour Ending'], y=data_2['Ambient Temp (°F)'], name = "Ambient Temp"),
                    secondary_y=True)
        fig.add_trace(go.Scatter(x=data_2['Hour Ending'], y=data_2['Submitted for Export to PCI'], name = "Submitted for Export to PCI"),
                    secondary_y=False)
        fig.update_layout(title_text = "<b>1X1 Capability Based on Forecasted Ambient Temp & Humidity</b>",
                    title_x = 0.5,xaxis_range = ["0","23"])
        fig.update_xaxes(title_text='Hour Ending', minor_ticks = 'inside')
        fig.update_yaxes(title_text = 'Output (MW)',minor_ticks = 'inside', secondary_y=False)
        fig.update_yaxes(title_text = 'Ambient Temp (°F)',minor_ticks = 'inside', secondary_y=True)
        fig.update_layout(legend = dict(orientation = "h",
                                x=0,
                                y=1.15,
                                title_font_family="Sitka Small",
                                bgcolor="LightBlue",
                                bordercolor="Black",
                                borderwidth=2))
        v2.write(fig)
else:
    data_2 = pd.read_csv("weather_data.csv") #working on here
    data_2['Hourly REG'] = 0
    data_2['Hourly Max'] = 0
    data_2['REG Max']  = np.where(select_evap=="IN", data_2['ch_in_d_off_1'], data_2['ch_out_d_off_1'])
    data_2 = data_2.assign(a = np.where(select_evap=='IN',data_2['ch_in_d_on_1'], data_2['ch_out_d_on_1']))
    data_2 = data_2.assign(b = np.where(data_2['a'] < DF_Max_1X1, data_2['a'],DF_Max_1X1))
    data_2 = data_2.assign(Max_Net_Gen = np.where(data_2['b'] > DF_Min_1X1, data_2['b'],DF_Min_1X1))                         
    data_2 = data_2.fillna(0)
    data_2['REG_to_PCI'] = data_2['REG Max'] + data_2['Hourly REG']
    data_2['Max_Net_PCI'] = data_2['Max_Net_Gen']+data_2['Hourly Max']
    data_2 = data_2.loc[:,['Hour','Temp', 'Humidity','REG Max','Hourly REG','REG_to_PCI','Max_Net_Gen','Hourly Max','Max_Net_PCI']]
    data_2 = data_2.rename(columns = {'Hour':'Hour Ending', 'Temp':'Ambient Temp (°F)','REG Max':'REG Max Generation Available (MW)','Hourly REG':'Hourly REG Max MW Bias','REG_to_PCI':
                                            'Max Net Generation Available','Hourly Max':'Hourly Max Net MW Bias','Max_Net_PCI':'Submitted for Export to PCI'})
    data_2 = data_2.round(decimals=0)
    data_2['Hourly REG Max MW Bias'] = data_2['Hourly REG Max MW Bias'].replace(0,"") #CHANGED HERE------------
    data_2['Hourly Max Net MW Bias'] = data_2['Hourly Max Net MW Bias'].replace(0,"")
    data_2.to_csv('data_2.csv')
    
    v1,v2 = st.columns(2)
    with v1:
        gd = GridOptionsBuilder.from_dataframe(data_2)
        gd.configure_pagination(enabled=True)
        gd.configure_side_bar()
        gd.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=False)
        gridoptions = gd.build()
        grid_table = AgGrid(data_2, gridOptions=gridoptions,
                                update_mode=GridUpdateMode.SELECTION_CHANGED,
                                allow_unsafe_jscode=True,
                                theme='balham',
                                fit_columns_on_grid_load=True)
        v1.download_button(label="Download CSV", data = data_2.to_csv(),  mime="text/csv")
    with v2:
        fig = make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(go.Scatter(x=data_2['Hour Ending'], y=data_2['REG Max Generation Available (MW)'], name = "REG Max Generation Available (MW)"),
                     secondary_y= False)
        fig.add_trace(go.Scatter(x=data_2['Hour Ending'], y=data_2['Ambient Temp (°F)'], name = "Ambient Temp"),
                    secondary_y=True)
        fig.add_trace(go.Scatter(x=data_2['Hour Ending'], y=data_2['Submitted for Export to PCI'], name = "Submitted for Export to PCI"),
                    secondary_y=False)
        fig.update_layout(title_text = "<b>1X1 Capability Based on Forecasted Ambient Temp & Humidity</b>",
                    title_x = 0.5,xaxis_range = ["0","23"])
        fig.update_xaxes(title_text='Hour Ending', minor_ticks = 'inside')
        fig.update_yaxes(title_text = 'Output (MW)',minor_ticks = 'inside', secondary_y=False)
        fig.update_yaxes(title_text = 'Ambient Temp (°F)',minor_ticks = 'inside', secondary_y=True)
        fig.update_layout(legend = dict(orientation = "h",
                                x=0,
                                y=1.15,
                                title_font_family="Sitka Small",
                                bgcolor="LightBlue",
                                bordercolor="Black",
                                borderwidth=2))
        v2.write(fig)

st.markdown("---")

st.markdown("<h2 style='text-align: center; color: black;'>PCI Data Summary</h1>", unsafe_allow_html=True)
data_1 = pd.read_csv("data_1.csv")
data_1["Unit"] = "HOT_SPR1 2x1"
data_1["Emergency Min (MW)"] = 300
data_1["Economic Min (MW)"] = 300
data_1["Regulation Min (MW)"] = 300
data_1["Economic Max (MW)"] = data_1['Max Net Generation Available']
data_1["Emergency Max (MW)"] = data_1['Max Net Generation Available']
data_1["Regulation Max (MW)"] = data_1['Max Net Generation Available']
data_1['Begin Date'] = str(select_date)+"  "+data_1['Hour Ending'].astype(str)+":00"
data_1 = data_1.loc[:,['Unit','Begin Date','Emergency Min (MW)',"Economic Min (MW)","Regulation Min (MW)","Regulation Max (MW)","Economic Max (MW)","Emergency Max (MW)"]]

data_1_b = pd.read_csv("data_1.csv")
data_1_b["Unit"] = "HOT_SPR1 2x1 DF"
data_1_b["Emergency Min (MW)"] = 300
data_1_b["Economic Min (MW)"] = 300
data_1_b["Regulation Min (MW)"] = 300
data_1_b["Economic Max (MW)"] = data_1_b['Submitted for Export to PCI']
data_1_b["Emergency Max (MW)"] = data_1_b['Submitted for Export to PCI']
data_1_b["Regulation Max (MW)"] = data_1_b['Max Net Generation Available'] #keep this
data_1_b['Begin Date'] = str(select_date)+"  "+data_1_b['Hour Ending'].astype(str)+":00"
data_1_b = data_1_b.loc[:,['Unit','Begin Date','Emergency Min (MW)',"Economic Min (MW)","Regulation Min (MW)","Regulation Max (MW)","Economic Max (MW)","Emergency Max (MW)"]]


data_2 = pd.read_csv("data_2.csv")
data_2["Unit"] = "HOT_SPR1 1x1"
data_2["Emergency Min (MW)"] = 125
data_2["Economic Min (MW)"] = 125
data_2["Regulation Min (MW)"] = 125
data_2["Economic Max (MW)"] = data_2['Max Net Generation Available']
data_2["Emergency Max (MW)"] = data_2['Max Net Generation Available']
data_2["Regulation Max (MW)"] = data_2['Max Net Generation Available']
data_2['Begin Date'] = str(select_date)+"  "+data_2['Hour Ending'].astype(str)+":00"
data_2 = data_2.loc[:,['Unit','Begin Date','Emergency Min (MW)',"Economic Min (MW)","Regulation Min (MW)","Regulation Max (MW)","Economic Max (MW)","Emergency Max (MW)"]]

data_2_b = pd.read_csv("data_2.csv")
data_2_b["Unit"] = "HOT_SPR1 1x1 DF"
data_2_b["Emergency Min (MW)"] = 125
data_2_b["Economic Min (MW)"] = 125
data_2_b["Regulation Min (MW)"] = 125
data_2_b["Economic Max (MW)"] = data_2_b['Submitted for Export to PCI']
data_2_b["Emergency Max (MW)"] = data_2_b['Submitted for Export to PCI']
data_2_b["Regulation Max (MW)"] = data_2_b['Max Net Generation Available']
data_2_b['Begin Date'] = str(select_date)+"  "+data_2_b['Hour Ending'].astype(str)+":00"
data_2_b = data_2_b.loc[:,['Unit','Begin Date','Emergency Min (MW)',"Economic Min (MW)","Regulation Min (MW)","Regulation Max (MW)","Economic Max (MW)","Emergency Max (MW)"]]

data_1_2 = pd.concat([data_2, data_2_b,data_1, data_1_b])
 
t1,t2,t3 = st.columns(3)
with t1:
    run = st.button('Preview Data to PCI', key ="16")
if run:
    gd = GridOptionsBuilder.from_dataframe(data_1_2)
    gd.configure_pagination(enabled=True)
    gd.configure_side_bar()
    gd.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=False)
    gridoptions = gd.build()
    grid_table = AgGrid(data_1_2, gridOptions=gridoptions,
                                update_mode=GridUpdateMode.SELECTION_CHANGED,
                                allow_unsafe_jscode=True,
                                theme='balham',
                                fit_columns_on_grid_load=True)

with t2:
   sav = st.button('Submit to PCI', key ="17")
if sav:
    from datetime import date
    currentDateTime = date.today()
    data_1_2.to_csv(f"C:/Users/HP User/OneDrive/Desktop/GIT/Submitted to PCI.csv",index=False)
t3.download_button(label="Download CSV", data = data_1_2.to_csv(),  mime="text/csv")








































