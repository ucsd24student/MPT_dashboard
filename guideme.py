import streamlit as st

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
        st.header("Forward Portfolio Dashboard", anchor=None, help=None, divider="gray")
        dashboard = """
                    Investing Analytics  developed the Forward Portfolio Dashboard initially for 
                    its own use to manage its own investment portfolio. Drs. Sklarz and Miller leveraged their 
                    decades of analyzing big and disparate data sets to stock investing, including utilizing machine
                    learning models and AI. A research team has now been assembled that is constantly improving the 
                    forward- looking valuation models.
                    """

        # Display the paragraph with the full-width styling
        st.markdown(f'<div class="full-width-paragraph">{dashboard}</div>', unsafe_allow_html=True)
        st.header("About Us", anchor=None, help=None, divider="gray")
        hanapepe = """Investing Analytics  was founded by Dr. Michael Sklarz. In collaboration with 
                    Dr. Norm Miller, Investing Analytics  developed the Forward Portfolio Dashboard. 
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
            # if st.button("Go Back"):
            #     mp.go_to_main_page()
            #     st.rerun()
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
                        cap company would generally be one worth less than $2 billion, a medium 
                        or mid-cap company is one between $2 billion and $10 billion in value and
                        a large cap is $10 billion and up.
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
