import streamlit as st
import pandas as pd
import mpt
import yfinance as yf

# Load the CSV data
csv_file = 'BCAstocks_8_27.csv'
indices = pd.read_csv('indices.csv')
df = pd.read_csv(csv_file)
# Display the full table
# st.write("Full Table")
# st.dataframe(df)

st.sidebar.header('Filter Options')

iv_values = st.sidebar.slider('Implied Volatility', 0.0, df['IV'].max(),value=[0.0,40.0])
tot_return_values = st.sidebar.slider('Forecasted Total Returns in %', 0.0, 200.0,value=[8.0,100.0])
# mar_cap_values = st.sidebar.slider('Market Cap in $Bn', 0.004, 3287.0,value=[0.01, 10.0])
etfs = ['All']
etfs.extend(df['Sector'].unique())
pe_values = st.sidebar.slider('Current PE Ratio', df['PE Ratio'].min(),df['PE Ratio'].max(),value=[6.0,80.0])
div_values = st.sidebar.slider('Dividend Yield in %', df['DividendYield'].min(),df['DividendYield'].max(),value=[0.01,5.0])
min_market = st.sidebar.number_input("Min Market Cap in $Mn ", min_value=0, max_value=3287000, value=10)
max_market = st.sidebar.number_input("Max Market Cap in $Mn", min_value=0, max_value=3287000, value=1000)
etf_selections = st.sidebar.multiselect('Select ETF',etfs,default='All')
idx = ['All','S&P 500', 'DJIA', 'Nasdaq 100']
idx_selection = st.sidebar.multiselect('Index',idx,default=['All'])

# Filter the dataframe based on user input
if iv_values:
    df = df[df['IV'].between(iv_values[0],iv_values[1])]

if tot_return_values:
    df = df[df['Total Return'].between(tot_return_values[0],tot_return_values[1])]

if min_market or max_market:
    df = df[df['Market Cap. (USD)'].between(min_market*1000000,max_market*1000000)]

if pe_values:
    df = df[df['PE Ratio'].between(pe_values[0],pe_values[1])]

if div_values:
    df = df[df['DividendYield'].between(div_values[0],div_values[1])]

if etf_selections and not 'All' in etf_selections:
    df = df[df['Sector'].isin(etf_selections)]

if idx_selection and not 'All' in idx_selection:
    tckr = set()
    for ind in idx_selection:
        tckr = tckr or set(indices[ind].dropna())
    df = df[df['Ticker'].isin(list(tckr))]

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
    st.metric(label='10Y Yield Rate', value=round(irate.info['regularMarketOpen'],2), delta=f"{chg}%")

# Display the filtered table
st.write("Filtered Table")
st.dataframe(df)

st.write("IV - Total Return")
chart_data = df[['IV', 'Total Return']]
st.scatter_chart(chart_data,x='IV',y='Total Return')

if 'clicked' not in st.session_state:
    st.session_state.clicked = False

def click_button():
    st.session_state.clicked = True

st.sidebar.button('Generate portfolio', on_click=click_button)

if st.session_state.clicked:
    ret, vol, wgts = mpt.generate_portfolio(df)
    frontier = pd.DataFrame([ret,vol])
    frontier = frontier.T
    frontier.columns = ['Expected Returns','Volatility']
    st.write("Efficient Frontier")
    st.scatter_chart(frontier,x='Volatility',y='Expected Returns')
    st.session_state.clicked = False
    # st.write('Allocations')
    # st.bar_chart(wgts,x='Ticker',y='Weights')
    # st.sidebar.write('Creating Portfolio')
