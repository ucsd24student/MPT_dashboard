import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from streamlit_plotly_events import plotly_events
import math
import mpt
import yfinance as yf

st.set_page_config(page_title="MPT Dashboard", page_icon=":chart:", layout="wide")

# Define a key in session state to track the current page
if "page" not in st.session_state:
    st.session_state.page = "main"  # Default page is the main dashboard

def go_to_main_page():
    st.session_state.page = "main"

# Button-click logic to navigate to the How-to page
def go_to_how_to_page():
    st.session_state.page = "howto"  # Change session state to the How-to page


def main_dashboard():
    # Load the CSV data
    csv_file = 'BCAstocks_9_23.csv'
    indices = pd.read_csv('indices.csv')
    df = pd.read_csv(csv_file).drop_duplicates()
    df = df[df['Total Return']>=0]
    backup_df = df
    # Display the full table
    # st.write("Full Table")
    # st.dataframe(df)

    if st.sidebar.button("Guide Me"):
        go_to_how_to_page()  # Button to switch to How-to page
        st.rerun()

    st.sidebar.header('Filter Options')

    iv_slider = st.sidebar.checkbox("Implied Volatility",help="Implied volatility: Reflects the market's forecast of a stock's potential price fluctuations, it is used as a measure to gauge market sentiment and risk.")
    if iv_slider:
        iv_values = st.sidebar.slider(' ',df['IV'].min(), df['IV'].max(),value=[0.0,40.0])

    returns_slider = st.sidebar.checkbox("Forecasted Total Returns in %",help="Total Returns: The projected return on an investment, combining both capital gains and dividends, reflecting the overall profitability expectation.")
    if returns_slider:
        tot_return_values = st.sidebar.slider(' ', df['Total Return'].min(), 300.0,value=[8.0,100.0])

    sharp_slider = st.sidebar.checkbox('Sharpe Ratio',help="Sharpe Ratio: Measures how well a stock’s returns compensate for its risk, with higher values indicating better risk-adjusted performance.")
    if sharp_slider:
        sharp_values = st.sidebar.slider(' ', df['Sharpe Ratio'].min(),df['Sharpe Ratio'].max(),value=[0.4,5.0])

    pe_slider = st.sidebar.checkbox('Current PE Ratio',help="PE Ratio: Indicates how much investors are willing to pay per dollar of earnings, helping to assess whether a stock is over or undervalued.")
    if pe_slider:
        pe_values = st.sidebar.slider(' ', df['PE Ratio'].min(),df['PE Ratio'].max(),value=[6.0,80.0])

    div_slider = st.sidebar.checkbox('Dividend Yield in %',help="Dividend Yield: Shows the annual dividend as a percentage of the stock’s current price, highlighting the income potential relative to the investment cost.")
    if div_slider:
        div_values = st.sidebar.slider(' ', df['DividendYield'].min(),df['DividendYield'].max(),value=[0.0,15.0])

    market_slider = st.sidebar.checkbox('Market Cap',help="Represents a company’s total value in the market, determined by multiplying share price by the number of outstanding shares.")
    if market_slider:
        # mar_cap_values = st.sidebar.slider('Market Cap in $Bn', 0.004, 3287.0,value=[0.01, 10.0])
        minm, maxm = st.sidebar.columns(2)
        with minm:
            min_market = st.sidebar.number_input("Min Market Cap in $Mn ", min_value=0, max_value=4000000, value=10)
        with maxm:
            max_market = st.sidebar.number_input("Max Market Cap in $Bn", min_value=0, max_value=4000, value=10)

    mavg = st.sidebar.checkbox('Price above 200 day MA',help="Indicates whether the current price of the stock is above 200 day moviing average.")

    etfs = ['All']
    etfs.extend(df['ETF'].dropna().unique())
    etf_selections = st.sidebar.multiselect('Select ETF',etfs)
    idx = ['S&P 500', 'DJIA', 'Nasdaq 100']
    idx_selection = st.sidebar.multiselect('Index',idx)

    allcs = st.sidebar.number_input('Maximum allocation per stock in %',min_value=2,max_value=20,value=10,help="Select the maximum limit of portfolio share per stock")


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

    def portfolio_button():
        if 'scatter_plot' in st.session_state:
            del st.session_state['scatter_plot']
        st.session_state.port_create = True

    # with table:
    st.sidebar.button('Generate portfolio', on_click=portfolio_button)

    # Display headers
    spy, dji, intrate = st.columns(3)

    with spy:
        sp500 = yf.Ticker("^SPX")
        chg = float(round((sp500.history()['Close'].iloc[-1] - sp500.history()['Close'].iloc[-2])/sp500.history()['Close'].iloc[-2]*100,2))
        st.metric(label='SPY', value=sp500.info['regularMarketOpen'], delta=f"{chg}%")

    with dji:
        djindex = yf.Ticker("^DJI")
        chg = float(round((djindex.history()['Close'].iloc[-1] - djindex.history()['Close'].iloc[-2])/djindex.history()['Close'].iloc[-2]*100,2))
        st.metric(label='DJI', value=djindex.info['regularMarketOpen'], delta=f"{chg}%")

    with intrate:
        irate = yf.Ticker("^TNX")
        chg = float(round((irate.history()['Close'].iloc[-1] - irate.history()['Close'].iloc[-2])/irate.history()['Close'].iloc[-2]*100,2))
        st.metric(label='10Y Yield Rate', value=round(irate.info['previousClose'],2), delta=f"{chg}%")
    

    # Display the filtered table
    table,scatter = st.columns(2,gap='medium')
    frontier_column, allocs_chart = st.columns(2,gap='medium')
    with table:
        st.write(f"Total Stocks: {len(df)}")
        st.dataframe(df.iloc[:,:-5], hide_index=True)
    # st.dataframe(df)

    with scatter:
        st.write("Implied Volatility - Total Return")
        fig = px.scatter(df, x='IV', y='Total Return', hover_data='Ticker')
        st.plotly_chart(fig)

    # chart_data = df[['IV', 'Total Return']]
    # st.scatter_chart(chart_data,x='IV',y='Total Return')

    if 'port_create' not in st.session_state:
        st.session_state.port_create = False

    if 'display' not in st.session_state:
        st.session_state.display = False

    frontier_chart = []
    # ret, vol, wgts = [], [], []
    @st.cache_data
    def generate_scatter_plot(df,allcs):
        ret, vol, wgts = mpt.generate_portfolio(df,allcs/100)
        frontier = pd.DataFrame([ret,vol])
        frontier_chart = frontier.T
        frontier_chart.columns = ['Expected Returns','Volatility']
        fig = px.scatter(frontier_chart,x='Volatility',y='Expected Returns',color=frontier_chart['Expected Returns']/frontier_chart['Volatility'],color_continuous_scale='viridis' )
        fig.update_coloraxes(colorbar_title='Sharpe Ratio')
        return fig, ret, vol, wgts

    # If filters change, scatter plot needs to update
    if 'scatter_plot' not in st.session_state:
        if st.session_state.port_create:
            st.session_state.scatter_plot, st.session_state.ret, st.session_state.vol, st.session_state.wgts = generate_scatter_plot(df,allcs)

    # Display scatter plot and handle click events
    if 'scatter_plot' in st.session_state:
        scatter_plot = st.session_state['scatter_plot']
        # Simulate an on_click event for scatter chart (replace with your own logic)
        with frontier_column:
            st.write("Efficient Frontier")
            selected_points = plotly_events(scatter_plot, click_event=True, hover_event=False, key='select_port')

        if selected_points:
            row_data = st.session_state.wgts.iloc[selected_points[0]['pointIndex'],:]
            row_df = pd.DataFrame(row_data)
            row_df = row_df[row_data > 0.01]*100
            with allocs_chart:
                st.write("Expected Return: ",selected_points[0]['y'],'\nVolatility: ',selected_points[0]['x'])
                st.bar_chart(row_df,y_label='Allocations in %')

def how_to_page():
    info, table = st.columns(2,gap='medium')
    st.markdown(
        """
        <style>
        .full-width-paragraph {
            width: 100%;  /* Makes the paragraph take up the full width */
            overflow: hidden;  /* Ensures no scrolling */
            word-wrap: break-word;  /* Break long words to fit in the container */
            white-space: normal;  /* Ensures paragraph will wrap */
            text-align: justify;  /* Justify text alignment */
        }

        .highlight {
            font-weight: bold;  /* Make highlighted words bold */
        }
        </style>
        """, 
        unsafe_allow_html=True
    )
    with info:
        st.header("Hanapepe Investment Dashboard", anchor=None, help=None, divider="gray")
        dashboard = """
                    Hanapepe Investments developed the Hanapepe Investment Dashboard (HID) initially for 
                    its own use to manage its own investment portfolio. Drs. Sklarz and Miller leveraged their 
                    decades of analyzing big and disparate data sets to stock investing, including utilizing machine
                    learning models and AI. A research team has now been assembled that is constantly improving the 
                    forward- looking valuation models.
                    """

# Display the paragraph with the full-width styling
        st.markdown(f'<div class="full-width-paragraph">{dashboard}</div>', unsafe_allow_html=True)
        st.header("About Us", anchor=None, help=None, divider="gray")
        hanapepe = """Hanapepe Investments was founded by Dr. Michael Sklarz. In collaboration with 
                    Dr. Norm Miller, Hanapepe Investments developed the Hanapepe Investment Dashboard, 
                    Dr. Sklarz is credited as one of the early founders of the automated valuation model (AVM) 
                    and is an expert in data and analytics. Through his company, Collateral Analytics, LLC, 
                    Dr. Sklarz licensed his AVM, as well as other derivative analytic products, to the financial 
                    industry, which including the largest banks in the United States. Dr. Sklarz sold his company
                    to Black Knight,Inc. in 2020, which was subsequently acquired by ICE, the Intercontinental 
                    Exchange, a financial services company, in 2023. Dr. Norm Miller was an esteemed faculty 
                    member at the University of San Diego in its real estate program. Dr. Miller was a 
                    high-recognized professor and the Ernst Hahn Chair of Real Estate Finance at USD. Prior to
                    joining USD, Dr. Miller was the academic director and the founder and center director of 
                    the real estate program at the University of Cincinnati."""
        st.markdown(f'<div class="full-width-paragraph">{hanapepe}</div>', unsafe_allow_html=True)
        st.header("Introduction to MPT", anchor=None, help=None, divider="gray")
        st.video("https://youtu.be/c5c_Zgn-Bjg?si=ZxdN_blklz0YUsPB", format="video/mp4", start_time=0, subtitles=None, end_time=None, loop=False, autoplay=False, muted=False)
        st.header("Our thoughts on effective use of the tool", anchor=None, help=None, divider="gray")
        combined_paragraphs = """
                                <div class="full-width-paragraph">
                                <span class="highlight">Investor Objectives:</span> <br>
                                Investor objectives can be broken down into at least two major
                                dimensions, income or growth in wealth such that future income will be derived. There may be
                                other specific objectives like protection from inflation or being able to save enough for grand
                                children’s college, but it all boils down to the desired timing of the future wealth derived by not
                                spending now and investing in assets that might provide a return. Generally early career people
                                want to focus more on long term growth, while older career types want to look for higher income
                                and less growth. It is impossible to have both, since the market bids for these assets and those
                                with more growth potential will be bid up relative to any current income. For this reason, many
                                stocks pay no dividends at all, since they want to reinvest and maximize growth potential. Other
                                stocks pay relatively high dividends while providing minimal growth.
                                </div>

                                <div class="full-width-paragraph">
                                <span class="highlight">Where should one invest? </span> <br>
                                Many investors already have savings accounts, CDs at banks, and
                                own a home, all of which is part of their personal portfolio. They may also own a whole life
                                insurance policy with a cash value and possibly less liquid investments like stamps, art,
                                antiques, or classic cars. But the entire spectrum of our portfolios might include cars,
                                collectibles, real estate, savings accounts, CDs, bonds, stocks or more. Generally, we divide up
                                our portfolio into that which is easily liquidated and that which is less liquid. The most liquid
                                investment would be a savings account or money market fund. Stocks tend to be very liquid.
                                Real estate investments are less liquid and may take months to convert to cash. How one
                                allocates their portfolio requires knowledge of the financial needs and optimal timing of the
                                household, as well as their risk tolerance. This requires an expert of some sort, such as a CFP,
                                certified financial professional, a CFA, certified financial analyst, possibly am SEC registered
                                investment advisor, or self-education in economics, finance, market systems and within each
                                investment type of interest.
                                </div>

                                <div class="full-width-paragraph">
                                We also divide up stocks into “growth” or “value” based on a simple formula, the average price
                                to earnings ratio or PE Ratio. Those stocks in the highest 50% of all stocks (higher PE ratios)
                                within any group or index are called growth stocks are called growth stocks, where the higher
                                the PE ratio the more the market feels they offer growth. The bottom half of the PE ratio list will
                                be called value stocks with the lower PE ratio stocks being more conservative investments with
                                less growth prospects. For example, a stock like a chip maker would be among the growth
                                stocks and a utility company or a REIT (real estate investment trust) would generally be among
                                the value stocks. We also divide stocks into various groups, like ETFs, see below, or by index
                                or country or exchange or whether they pay dividends or not, or whether they trade in US
                                dollars or other currency.
                                </div>

                                <div class="full-width-paragraph">
                                There are some investments that pay nothing in dividends and have no sales data available on
                                which to judge future growth, for example cryptocurrencies or gold. These are not investments
                                we follow or provide information about.
                                </div>
                                """

        # Display all paragraphs under a single markdown block
        st.markdown(combined_paragraphs, unsafe_allow_html=True)

        with table:
            if st.button("Go Back"):
                go_to_main_page()
                st.rerun()
            st.header("More information on fundamental factors", anchor=None, help=None, divider="gray")
            with st.expander("Implied Volatility"):
                st.write('''
                        We use the implied volatility from forward looking options about one year out
                        for this measurement. If a stock has no options trading, then we either do not include it or use
                        the historical standard deviation of total returns for that stock.\n 
                        Many firms use historical volatility or some number
                        of recent years, but we prefer a forward-looking measure of IV. Note that one should not
                        trust extremely low IVs for a portfolio, in that the correlations next year could easily be
                        less negative than those assumed in our calculations and if so, the risks will be higher
                        than if based on the recent market metrics. It is easy to generate a very appealing and
                        low risk portfolio if we were certain about the correlations between stock returns, but we
                        are not certain.
                        ''')
            
            with st.expander("Forecast Total Returns in Percent"):
                st.write('''
                        We use the expected price one year out plus dividends to
                        generate a ‘target expected return'.
                        ''')
            with st.expander("Sharpe Ratio"):
                st.write('''
                        We use the concept of the [Sharpe ratio](https://www.investopedia.com/terms/s/sharperatio.asp) 
                        by Economit [William F Sharpe](https://www.investopedia.com/terms/w/william-f-sharpe.asp) but 
                        redefine it in the Hanapepe Investment Dashboard.
                        We use target returns, based on either the aggregate average of professional analysts, plus
                        dividends expected over the next year to define a target one year return, or we use our own
                        proprietary AI modeling to forecast the stock price one year ahead and add dividends (at current
                        rates) to define the one-year target return.'.
                        ''')

            with st.expander("Current PE Ratio"):
                st.write('''
                        This is the current stock price over the current stated earnings.
                        ''')

            with st.expander("Dividend Yield in Percent"):
                st.write('''
                        This is the annualized dividends, if any, over the current stock price.
                        ''')

            with st.expander("Target Price"):
                st.write('''
                        This is the target mean price of all analysts in version one of the dashboard
                        and in version two, an AI based target price, where we use six different models to
                        forecast the stock price one year out.
                        ''')
             
            with st.expander("Percent from Target"):
                st.write('''
                        Based on the target price used, we calculate the difference
                        between that and the current price.
                        ''')

            with st.expander("Last price"):
                st.write('''
                        This is the most recent traded price for the stock.
                        ''')

            with st.expander("Total Expected Return"):
                st.write('''
                        The total one year expected return is the sum of the change in
                        price plus dividends over the current price.
                        ''')
             
            with st.expander("Exchange"):
                st.write('''
                        This is the exchange such as the New York Stock Exchange or NASDAQ or
                        others.
                        ''')

            with st.expander("Market Capitalization"):
                st.write('''
                        This is the sum of the outstanding stock shares times the current price. 
                        This is calculcated as the sum of the value of all stock, whether traded 
                        or not, at current prices times the number of shares outstanding. A small
                        cap company would generally be one worth less than \$2 billion, a medium 
                        or mid-cap company is one between \$2 billion and \$10 billion in value and
                        a large cap is \$10 billion and up.
                        ''')
 
            with st.expander("Price above 200 day moving average"):
                st.write('''
                        Stock prices can be viewed relative to their historical trend. If a stock
                        is above it’s 200 day moving average then one can check this filter. In 
                        this case, the price is relatively high or moving up compared to the last 
                        200 days. This is considered a technical filter as opposed to a fundamental 
                        filter, such as price to earnings.
                        ''')

            with st.expander("ETF"):
                st.write('''
                        This is an exchange traded fund and generally it is focused on a specific sector,
                        although there are broad market ETFs as well.
                        ''')

            with st.expander("Index"):
                st.write('''
                        This is based on the stock exchange such as the New York Stock Exchange
                        NYSE) or the NASDAQ.
                        ''')
            
            with st.expander("Industry"):
                st.write('''
                        There are 25 industry groups used by the global industry standards.
                        1. Automobiles and Components\n
                        2. Banks\n
                        3. Capital Goods\n
                        4. Commercial and Professional Services\n
                        5. Consumer Discretionary Distribution and Retail\n
                        6. Consumer Durables and Apparel\n
                        7. Consumer Staples Distribution and Retail\n
                        8. Consumer Services\n
                        9. Energy\n
                        10. Equity Real Estate Investment Trusts (REITs)\n
                        11. Financials Services\n
                        12. Food, Beverage, and Tobacco\n
                        13. Health Care Equipment and Services\n
                        14. Household and Personal Products\n
                        15. Insurance\n
                        16. Materials\n
                        17. Media and Entertainment\n
                        18. Pharmaceuticals, Biotechnology, and Life Sciences\n
                        19. Real Estate Management and Development\n
                        20. Semiconductors and Semiconductor Equipment\n
                        21. Software and Services\n
                        22. Technology Hardware and Equipment\n
                        23. Telecommunication Services\n
                        24. Transportation\n
                        25. Utilities\n
                        ''')

            with st.expander("Sector"):
                st.write('''
                        There are 11 stock sectors.
                        1. Energy (XLE)\n
                        2. Materials (XLB)\n
                        3. Industrials (XLI)\n
                        4. Utilities (XLU)\n
                        5. Healthcare (XLV)\n
                        6. Financials (XLF)\n
                        7. Consumer Discretionary (XLY)\n
                        8. Consumer Staples (XLP)\n
                        9. Information Technology (XLK)\n
                        10. Communication Services (XLC)\n
                        11. Real Estate (XLRE)\n
                        ''')

                        

# Page navigation logic
if st.session_state.page == "main":
    main_dashboard()  # Display the main dashboard
elif st.session_state.page == "howto":
    how_to_page()  # Display the How-to page
