import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_plotly_events import plotly_events
import plotly.graph_objs as go
import mpt
import custom
import yfinance as yf
import guideme
import time

def main():
    try:
        st.set_page_config(layout="wide")
    except:
        temp = None
    # st.session_state.page = st.sidebar.selectbox("Navigate to", ["Dashboard","My Portfolio", "Guide Me"],index=0)
    if 'page' not in st.session_state:
        st.session_state.page = "Dashboard"
    st.sidebar.button("Dashboard",key="db")
    st.sidebar.button("My Portfolio",key="myport")
    # st.sidebar.button("Guide Me",key="help")

    left,center,right = st.columns(3,gap='large')

    # with left:
    #     dashb,myport,gme = st.columns(3,gap='small')
    #     with dashb:
    #         st.button("Dashboard",key="db")
            
    #     with myport:
    #         st.button("My Portfolio",key="myport")
    with right:
        dash,myp,gm = st.columns(3,gap='small')
    #     with dash:
    #         st.button("Dashboard",key="db")
            
    #     with myp:
    #         st.button("My Portfolio",key="myport")
        
        with gm:
            st.button("Guide Me",key="help")

    if "db" in st.session_state and st.session_state.db:
        st.session_state.page = "Dashboard"
    elif "myport" in st.session_state and st.session_state.myport:
        st.session_state.page = "My Portfolio"
    elif "help" in st.session_state and st.session_state.help:
        st.session_state.page = "Guide Me"

    navigate(st.session_state.page)
    
def navigate(page):
    theme = True
    title_color = 'White' if theme else 'Black'
    if page == "Dashboard":
        st.markdown(f"<h1 style='text-align: center; color: {title_color};'>Forward Portfolio Dashboard</h1>", unsafe_allow_html=True)
        main_dashboard()
    elif page == "My Portfolio":
        st.markdown(f"<h1 style='text-align: center; color: {title_color};'>My Portfolio</h1>", unsafe_allow_html=True)
        st.cache_data.clear()
        custom.build_custom()
    elif page == "Guide Me":
        st.markdown(f"<h1 style='text-align: center; color: {title_color};'>Guide Me</h1>", unsafe_allow_html=True)
        guideme.how_to_page()


def portfolio_button():
    if 'scatter_plot' in st.session_state:
        del st.session_state['scatter_plot']
    st.session_state.port_create = True

def custom_page():
    st.session_state.custom_pg = True

# Function to get Plotly theme settings dynamically
def get_plotly_theme_settings():
    theme = st.config.get_option("theme.base")
    is_dark = theme == "dark" 
    return is_dark

# @st.cache_data
def generate_scatter_plot(df,allcs):
    df = df[df['Total Return']>=0]
    try:
        ret, vol, wgts = mpt.generate_portfolio(df,allcs/100)
    except Exception as e:
        st.error(f"Something didn't go right please contact support with the error message! \n Error: {e}")
        st.stop()
    frontier = pd.DataFrame([ret,vol])
    frontier_chart = frontier.T
    frontier_chart.columns = ['Expected Returns','Volatility']
    if frontier_chart['Volatility'].min()>=40:
        frontier_chart['Volatility'] /= 10
    frontier_chart = frontier_chart[frontier_chart['Volatility']<=150].round(2)
    extreme_low = frontier_chart[(frontier_chart['Volatility']>=0.25*frontier_chart['Volatility'].max()) & (frontier_chart['Expected Returns']<=0.15*frontier_chart['Expected Returns'].max())]
    frontier_chart = frontier_chart[~frontier_chart.isin(extreme_low).all(axis=1)]
    # theme = get_plotly_theme_settings() #dynamic theme update -- to be implemented
    color_scale = 'YlGn' #if theme else 'viridis'
    template = 'plotly_dark' #if theme else 'plotly_white'
    fig = px.scatter(frontier_chart,x='Volatility',y='Expected Returns',template=template,color=frontier_chart['Expected Returns']/frontier_chart['Volatility'],color_continuous_scale=color_scale )
    fig.update_coloraxes(colorbar_title='Sharpe Ratio')
    fig.add_trace(go.Scatter(
                    x=frontier_chart['Volatility'], 
                    y=frontier_chart['Expected Returns'], 
                    mode='lines',  # This ensures it's plotted as a line
                    line_shape='spline',  # Smooth curve (spline)
                    line=dict(color='#C9FBE5', width=2),
                    name='Frontier Line',
                    showlegend=True,
                    legendgroup='line'
                )
            )
    fig.update_traces(marker=dict(size=12), selector=dict(mode='markers'))
    fig.update_layout(coloraxis_colorbar=dict(title="Sharpe Ratio"),
                        legend=dict(
                            yanchor="top", 
                            y=0.98,  # Position the added elements legend separately
                            xanchor="left", 
                            x=0.02
                        ),
                        autosize=True,
                        margin=dict(l=0, r=0)
                    )
    return fig, ret, vol, wgts

def main_dashboard():
    # Load the CSV data
    csv_file = 'stock_data.csv'
    indices = pd.read_csv('indices.csv')
    df = pd.read_csv(csv_file).drop_duplicates()

    # if st.sidebar.button("Guide Me"):
    #     mp.go_to_how_to_page()  # Button to switch to How-to page
    #     st.rerun()


    st.sidebar.header('Filter Options')

    iv_slider = st.sidebar.checkbox("Implied Volatility", key='key' ,help="Implied volatility: Reflects the market's forecast of a stock's potential price fluctuations, it is used as a measure to gauge market sentiment and risk.")
    if iv_slider:
        iv_values = st.sidebar.slider(' ',df['IV'].min(), df['IV'].max(),value=[0.0,40.0])

    returns_slider = st.sidebar.checkbox("Forecasted Total Returns in %", key='retn',help="Total Returns: The projected return on an investment, combining both capital gains and dividends, reflecting the overall profitability expectation.")
    if returns_slider:
        tot_return_values = st.sidebar.slider(' ', df['Total Return'].min(), 300.0,value=[8.0,100.0])

    sharp_slider = st.sidebar.checkbox('Sharpe Ratio', key='sr',help="Sharpe Ratio: Measures how well a stock’s returns compensate for its risk, with higher values indicating better risk-adjusted performance.")
    if sharp_slider:
        sharp_values = st.sidebar.slider(' ', df['Sharpe Ratio'].min(),df['Sharpe Ratio'].max(),value=[0.4,5.0])

    pe_slider = st.sidebar.checkbox('Current PE Ratio', key='pe',help="PE Ratio: Indicates how much investors are willing to pay per dollar of earnings, helping to assess whether a stock is over or undervalued.")
    if pe_slider:
        pe_values = st.sidebar.slider(' ', df['PE Ratio'].min(),df['PE Ratio'].max(),value=[6.0,80.0])

    div_slider = st.sidebar.checkbox('Dividend Yield in %', key='dy',help="Dividend Yield: Shows the annual dividend as a percentage of the stock’s current price, highlighting the income potential relative to the investment cost.")
    if div_slider:
        div_values = st.sidebar.slider(' ', df['DividendYield'].min(),df['DividendYield'].max(),value=[0.0,15.0])

    market_slider = st.sidebar.checkbox('Market Cap', key='mc',help="Represents a company’s total value in the market, determined by multiplying share price by the number of outstanding shares.")
    if market_slider:
        # mar_cap_values = st.sidebar.slider('Market Cap in $Bn', 0.004, 3287.0,value=[0.01, 10.0])
        minm, maxm = st.sidebar.columns(2)
        with minm:
            min_market = st.sidebar.number_input("Min Market Cap in $Mn ", min_value=0, max_value=4000000, value=10,key='mincap')
        with maxm:
            max_market = st.sidebar.number_input("Max Market Cap in $Bn", min_value=0, max_value=4000, value=10,key='maxcap')

    mavg = st.sidebar.checkbox('Price above 200 day MA', key='mav',help="Indicates whether the current price of the stock is above 200 day moviing average.")

    etfs = ['All']
    etfs.extend(df['ETF'].dropna().unique())
    etf_selections = st.sidebar.multiselect('Select ETF',etfs,key='etf')
    idx = ['S&P 500', 'DJIA', 'Nasdaq 100']
    idx_selection = st.sidebar.multiselect('Index',idx,key='idx')

    allcs = st.sidebar.number_input('Maximum allocation per stock in %',min_value=2,max_value=20,value=10,help="Select the maximum limit of portfolio share per stock",key='alloc')


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

    # with table:
    st.sidebar.button('Generate portfolio', on_click=portfolio_button,key='port')

    # Display headers
    spy, dji, intrate = st.columns(3)

    with spy:
        sp500 = yf.Ticker("^SPX")
        try:
            chg = float(round((sp500.history()['Close'].iloc[-1] - sp500.history()['Close'].iloc[-2])/sp500.history()['Close'].iloc[-2]*100,2))
            st.metric(label='SPY', value=sp500.info['open'], delta=f"{chg}%")
        except:
            time.sleep(0.01)
            chg = float(round((sp500.history()['Close'].iloc[-1] - sp500.history()['Close'].iloc[-2])/sp500.history()['Close'].iloc[-2]*100,2))
            st.metric(label='SPY', value=sp500.info['open'], delta=f"{chg}%")

    with dji:
        djindex = yf.Ticker("^DJI")
        try:
            chg = float(round((djindex.history()['Close'].iloc[-1] - djindex.history()['Close'].iloc[-2])/djindex.history()['Close'].iloc[-2]*100,2))
            st.metric(label='DJI', value=djindex.info['open'], delta=f"{chg}%")
        except:
            time.sleep(0.01)
            chg = float(round((djindex.history()['Close'].iloc[-1] - djindex.history()['Close'].iloc[-2])/djindex.history()['Close'].iloc[-2]*100,2))
            st.metric(label='DJI', value=djindex.info['open'], delta=f"{chg}%")

    with intrate:
        irate = yf.Ticker("^TNX")
        try:
            chg = float(round((irate.history()['Close'].iloc[-1] - irate.history()['Close'].iloc[-2])/irate.history()['Close'].iloc[-2]*100,2))
            st.metric(label='10Y Yield Rate', value=round(irate.info['open'],2), delta=f"{chg}%")
        except:
            time.sleep(0.01)
            chg = float(round((irate.history()['Close'].iloc[-1] - irate.history()['Close'].iloc[-2])/irate.history()['Close'].iloc[-2]*100,2))
            st.metric(label='10Y Yield Rate', value=round(irate.info['open'],2), delta=f"{chg}%")
    

    # Display the filtered table
    table,scatter = st.columns(2,gap='medium')
    frontier_column, allocs_chart = st.columns(2,gap='medium')
    with table:
        st.header("Information Table")
        st.write(f"Total Stocks: {len(df)}")
        st.write(f"Total Stocks with Positive Total Returns: {len(df[df['Total Return']>=0])}")
        st.dataframe(df.iloc[:,:-5], hide_index=True)
    # st.dataframe(df)

    with scatter:
        st.header("Spread")
        st.write("Implied Volatility - Total Return")
        fig = px.scatter(df[df['Total Return']>=0], x='IV', y='Total Return', hover_data='Ticker')
        st.plotly_chart(fig)

    if 'port_create' not in st.session_state:
        st.session_state.port_create = False

    if 'custom_pg' not in st.session_state:
        st.session_state.custom_pg = False

    if 'display' not in st.session_state:
        st.session_state.display = False

    # If filters change, scatter plot needs to update
    if 'scatter_plot' not in st.session_state:
        if st.session_state.port_create:
            st.session_state.scatter_plot, st.session_state.ret, st.session_state.vol, st.session_state.wgts = generate_scatter_plot(df,allcs)

    # Display scatter plot and handle click events
    if 'scatter_plot' in st.session_state:
        scatter_plot = st.session_state['scatter_plot']
        # Simulate an on_click event for scatter chart (replace with your own logic)
        with frontier_column:
            st.header("Efficient Frontier")
            selected_points = plotly_events(scatter_plot, click_event=True, hover_event=False, key='select_port')

        if selected_points:
            try:
                row_data = st.session_state.wgts.iloc[selected_points[0]['pointIndex'],:]
            except:
                row_data = st.session_state.wgts.iloc[0,:]
            row_df = pd.DataFrame(row_data)
            row_df = row_df[row_data > 0.01]*100
            with allocs_chart:
                st.header("Allocations")
                st.write("Expected Return: ",selected_points[0]['y'],'\nVolatility: ',selected_points[0]['x'])
                st.bar_chart(row_df,y_label='Allocations in %')

if __name__ == "__main__":
    main()
