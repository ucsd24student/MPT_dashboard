import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import math
import mpt
import yfinance as yf

# Load the CSV data
csv_file = 'BCAstocks_9_23.csv'
indices = pd.read_csv('indices.csv')
df = pd.read_csv(csv_file)
backup_df = df
# Display the full table
# st.write("Full Table")
# st.dataframe(df)

st.sidebar.header('Filter Options')

iv_slider = st.sidebar.checkbox("Implied Volatility")
if iv_slider:
    iv_values = st.sidebar.slider('',df['IV'].min(), df['IV'].max(),value=[0.0,40.0])

returns_slider = st.sidebar.checkbox("Forecasted Total Returns in %")
if returns_slider:
    tot_return_values = st.sidebar.slider('', df['Total Return'].min(), 300.0,value=[8.0,100.0])

sharp_slider = st.sidebar.checkbox('Sharpe Ratio')
if sharp_slider:
    sharp_values = st.sidebar.slider('', df['Sharpe Ratio'].min(),df['Sharpe Ratio'].max(),value=[0.4,5.0])

pe_slider = st.sidebar.checkbox('Current PE Ratio')
if pe_slider:
    pe_values = st.sidebar.slider('', df['PE Ratio'].min(),df['PE Ratio'].max(),value=[6.0,80.0])

div_slider = st.sidebar.checkbox('Dividend Yield in %')
if div_slider:
    div_values = st.sidebar.slider('', df['DividendYield'].min(),df['DividendYield'].max(),value=[0.0,15.0])

market_slider = st.sidebar.checkbox('Market Cap')
if market_slider:
    # mar_cap_values = st.sidebar.slider('Market Cap in $Bn', 0.004, 3287.0,value=[0.01, 10.0])
    minm, maxm = st.sidebar.columns(2)
    with minm:
        min_market = st.sidebar.number_input("Min Market Cap in $Mn ", min_value=0, max_value=4000000, value=10)
    with maxm:
        max_market = st.sidebar.number_input("Max Market Cap in $Bn", min_value=0, max_value=4000, value=10)

mavg = st.sidebar.checkbox('Price above 200 day MA')

etfs = ['All']
etfs.extend(df['ETF'].dropna().unique())
etf_selections = st.sidebar.multiselect('Select ETF',etfs)
idx = ['S&P 500', 'DJIA', 'Nasdaq 100']
idx_selection = st.sidebar.multiselect('Index',idx)


# reset,portfolio = st.sidebar.columns(2)
# with reset: 
# st.sidebar.button('Reset filters',on_click=no_filter)

# Filter the dataframe based on user input
if iv_slider:
    df = df[df['IV'].between(iv_values[0],iv_values[1])]

if returns_slider:
    df = df[df['Total Return'].between(tot_return_values[0],tot_return_values[1])]

if sharp_slider:
    df = df[df['Sharpe Ratio'].between(sharp_values[0],sharp_values[1])]

if pe_slider:
    df = df[df['PE Ratio'].between(pe_values[0],pe_values[1])]

if div_slider:
    df = df[df['DividendYield'].between(div_values[0],div_values[1])]

if market_slider:
    df = df[df['Market Cap. (USD)'].between(min_market*1000000,max_market*1000000000)]

if etf_selections and not 'All' in etf_selections:
    df = df[df['ETF'].isin(etf_selections)]

if idx_selection:
    tckr = []
    for ind in idx_selection:
        # df = df[df[ind]==ind]
        tckr.extend(indices[ind].dropna())
    fticks = list(set(df['Ticker']) and set(tckr))
    df = df[df['Ticker'].isin(fticks)]

if mavg:
    df = df[df['Price Above 200 MAV']=='YES']

def no_filter():
    st.session_state.filter_reset = True

def portfolio_button():
    st.session_state.port_create = True

# with table:
# st.sidebar.button('Reset Filters', on_click=no_filter)
st.sidebar.button('Generate portfolio', on_click=portfolio_button)

# if 'filter_reset' not in st.session_state:
#     st.session_state.filter_reset = False

# if st.session_state.filter_reset:
#     df = backup_df

# Display headers
spy, dji, intrate = st.columns(3)

with spy:
    sp500 = yf.Ticker("SPY")
    chg = float(round((sp500.history()['Close'].iloc[-1] - sp500.history()['Close'].iloc[-2])/sp500.history()['Close'].iloc[-2]*100,2))
    st.metric(label='SPY', value=sp500.info['regularMarketOpen'], delta=f"{chg}%")

with dji:
    djindex = yf.Ticker("^DJI")
    chg = float(round((djindex.history()['Close'].iloc[-1] - djindex.history()['Close'].iloc[-2])/djindex.history()['Close'].iloc[-2]*100,2))
    st.metric(label='DJI', value=djindex.info['regularMarketOpen'], delta=f"{chg}%")

with intrate:
    irate = yf.Ticker("^TYX")
    chg = float(round((irate.history()['Close'].iloc[-1] - irate.history()['Close'].iloc[-2])/irate.history()['Close'].iloc[-2]*100,2))
    st.metric(label='10Y Yield Rate', value=round(irate.info['previousClose'],2), delta=f"{chg}%")

# Display the filtered table
# table,chart = st.columns(2,gap='medium')
# with table:
st.write(f"Total Stocks: {len(df)}")
st.dataframe(df.iloc[:,:-5], hide_index=True)
# st.dataframe(df)

# with chart:
st.write("Implied Volatility - Total Return")
fig = px.scatter(df, x='IV', y='Total Return', hover_data='Ticker')
st.plotly_chart(fig)

# chart_data = df[['IV', 'Total Return']]
# st.scatter_chart(chart_data,x='IV',y='Total Return')

if 'port_create' not in st.session_state:
    st.session_state.port_create = False

if st.session_state.port_create:
    ret, vol, wgts = mpt.generate_portfolio(df)
    frontier = pd.DataFrame([ret,vol])
    frontier = frontier.T
    frontier.columns = ['Expected Returns','Volatility']
    st.write("Efficient Frontier")
    st.scatter_chart(frontier,x='Volatility',y='Expected Returns')
    st.session_state.clicked = False
    lbl = [f'{ret[i]}_{vol[i]}' for i in range(len(ret))]
    # print(wgts.index.values(),wgts.columns.values())
    # wgts.reset_index().to_csv('weights.csv',index=False)
    st.write('Allocations')
    row_data = wgts.iloc[math.floor(len(wgts)/2),:]
    row_df = pd.DataFrame(row_data)
    row_df = row_df[row_data > 0.01]*100
    st.bar_chart(row_df,y_label='Allocations in %')
    st.session_state.port_create = False
    # fig, ax = plt.subplots()
    # ax.bar(row_data.index, row_data.values)
    # ax.set_xlabel('Ticker')
    # ax.set_ylabel('Allocations')
    # st.pyplot(fig)
