import streamlit as st
import pandas as pd
import mpt
from io import BytesIO
import plotly.express as px
import plotly.graph_objs as go
from streamlit_plotly_events import plotly_events
import yfinance as yf

# TO BE IMPLEMENTED
# # To maintain data in each tab
# def tab_flag():
#     if 'tflag' in st.session_state and st.session_state.tflag:
#         st.session_state.assets_data.drop(st.session_state.assets_data.index , inplace=True)
#         print(st.session_state.assets_data.shape)
#         st.session_state.tflag = False

def check_yf(input_data,df):
    flag = False
    for tck in input_data[~(input_data['Asset'].isin(df['Ticker']))]['Asset']:
        try:
            yf.Ticker(tck).info['shortName']
            st.error(f"Currently we do not have {tck} in our database. We'll soon include that.")
            flag = True
        except:
            input_data = input_data.drop(input_data[input_data['Asset']==tck].index)
        st.stop() if flag else None
    return input_data

@st.cache_data
def data_validation(input_data,df):
    if input_data.columns[0] in df['Ticker']:
        no_head = pd.DataFrame([df.columns], columns=df.columns)
        input_data = pd.concat([no_head, input_data]).reset_index(drop=True)
        
    input_data = input_data.drop(input_data.columns[2:], axis=1)
    input_data.columns = ['Asset','Allocation']
    input_data = check_yf(input_data,df)
    input_data.dropna(inplace=True)
    input_data.drop_duplicates(subset='Asset', inplace=True)
    input_data['Allocation'] = input_data['Allocation'].astype(float).round(2)

    if input_data['Allocation'].sum() >= 95.0 and input_data['Allocation'].sum() < 99.5:
        st.warning(f"You have entered {input_data['Allocation'].sum()}% of your portfolio. Remaining would be assumed to be cash")
    elif round(input_data['Allocation'].sum(),2) >= 99.5 and round(input_data['Allocation'].sum(),2) <= 100.5:
        None
    else:
        st.error("Allocations do not consolidate to 100%. Please recheck the weights and reupload.")
        st.session_state.compare_port = False
        return None
    return input_data

# Callback function to reset the selectbox after a selection
def reset_selectbox():
    # Update the selected options into session state
    st.session_state.asset = st.session_state.asset_selection
    st.session_state.allocation = st.session_state.alloc_selection
    # Reset the selectbox and number input values (to show the placeholders again)
    st.session_state.asset_selection = None
    st.session_state.alloc_selection = None
    assets = pd.DataFrame({'Asset':[st.session_state.asset],'Allocation':[st.session_state.allocation]})
    st.session_state.assets_data = pd.concat([st.session_state.assets_data, assets], ignore_index=True)

def call_mpt():
    if st.session_state.assets_data.shape[0] != 0:
        st.session_state.compare_port = True
        
def scatter_plot_custom(df,curr_ret,curr_vol,rf_rate,bound):
    try:
        ret, vol, wgts = mpt.generate_portfolio(df,bound)
    except Exception as e:
        st.error(f"Something didn't go right in GC please contact support with the error message! \n Error: {e}")
        st.stop()
    frontier = pd.DataFrame([ret,vol])
    frontier_chart = frontier.T
    frontier_chart.columns = ['Expected Returns','Volatility']

    if frontier_chart['Volatility'].min()>=40:
        frontier_chart['Volatility'] /= 10
    curr_vol /= 10 if curr_vol > frontier_chart['Volatility'].mean() else curr_vol
    frontier_chart = frontier_chart[frontier_chart['Volatility']<=150]
    frontier_sharpe = (frontier_chart['Expected Returns'] - rf_rate)/frontier_chart['Volatility']
    
    fig = px.scatter(frontier_chart,x='Volatility',y='Expected Returns',template="plotly_dark",color=frontier_sharpe,color_continuous_scale='YlGn' )
    fig.add_scatter(x=[curr_vol], y=[curr_ret], mode='markers', marker=dict(symbol='square', size=12, color='red'),
                name="Your portfolio",showlegend=True,legendgroup='custom')
    fig.add_trace(go.Scatter(
                    x=frontier_chart['Volatility'], 
                    y=frontier_chart['Expected Returns'], 
                    mode='lines', 
                    line_shape='spline', 
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
                            y=0.98, 
                            xanchor="left", 
                            x=0.02
                        ),
                        autosize=True,
                        margin=dict(l=0, r=0)
                    )
    
    return fig,wgts

def build_custom():
    df = pd.read_csv('stock_data.csv').drop_duplicates()
    history = pd.read_csv('bayesian_forecast.csv')
    try:
        st.set_page_config(layout="wide")
    except:
        None

    # Initialize session state variables
    if 'asset_selection' not in st.session_state:
        st.session_state.asset_selection = None
    if 'alloc_selection' not in st.session_state:
        st.session_state.alloc_selection = None
    if 'asset' not in st.session_state:
        st.session_state.asset = None
    if 'allocation' not in st.session_state:
        st.session_state.allocation = None
    if 'assets_data' not in st.session_state:
        st.session_state.assets_data = pd.DataFrame(columns=['Asset', 'Allocation']) 
    # if 'tflag' not in st.session_state:
    #     st.session_state.tflag = False

    inp,tools = st.columns(2,gap='large')
    with inp:
        option1,option2 = st.tabs(['File upload','Manual Input'])
        with option1:
            lbl,pover = st.columns(2,gap='large')
            with lbl:
                st.subheader("Add your portfolio")
            with pover:
                with st.popover("Example file"):
                    example = pd.DataFrame({'Assets':['AAPL','MSFT','NVDA'],
                                            'Allocation':[15.50,8.92,22.81]})
                    st.dataframe(example)
            st.write('Note - The file should be in the format .csv/.xlsx/.txt with only 2 columns including the asset symbol(Eg. AAPL , MSFT) and its allocation in percent format as decimal numbers. Sum of allocation should be 100.0')
            uploaded_file = st.file_uploader(" ",type=["csv","xlsx","xls","txt"])
            dataframe = None
            if uploaded_file is not None:
                if uploaded_file.type == 'text/plain':
                    try:
                        dataframe = pd.read_csv(uploaded_file, sep="\t")
                    except:
                        try:
                            dataframe = pd.read_csv(uploaded_file, sep=",")
                        except:
                            st.error('Error reading file, upload the txt file with tab or comma delimiter')
                            uploaded_file = None

                elif uploaded_file.type == 'text/csv':
                    try:
                        dataframe = pd.read_csv(uploaded_file)
                    except:
                        st.error('Error reading file, upload the csv file with tab or comma delimiter')
                        uploaded_file = None

                elif 'application' in uploaded_file.type:
                    try:
                        # To read file as bytes:
                        bytes_data = uploaded_file.getvalue()
                        excel_data = BytesIO(bytes_data)
                        sheets = pd.ExcelFile(excel_data)
                        dataframe = sheets.parse(sheets.sheet_names[0])
                    except Exception as e:
                        st.error(f'Error reading file, upload an excel sheet with tab or comma delimiter{e}')
                        uploaded_file = None

                if uploaded_file: 
                    dataframe = data_validation(dataframe,df)
                    if dataframe is not None:
                        st.session_state.assets_data = dataframe
                        st.session_state.assets_data.index += 1
                        maxall = st.session_state.assets_data['Allocation'].max()
                        maxlim = maxall + 5 - (maxall % 5)
                        st.session_state.assets_data['Minimum Allocation'] = 0.0
                        st.session_state.assets_data['Maximum Allocation'] = float(maxlim)

                        st.session_state.assets_data = st.data_editor(st.session_state.assets_data,
                                            column_config={
                                                "Minimum Allocation": st.column_config.NumberColumn(
                                                    "Minimum Allocation",
                                                    # help="",
                                                    min_value=0,
                                                    max_value=100,
                                                    step=0.01,
                                                    format="%2f"
                                                ),
                                                "Maximum Allocation": st.column_config.NumberColumn(
                                                    "Maximum Allocation",
                                                    # help="",
                                                    min_value=0,
                                                    max_value=100,
                                                    step=0.01,
                                                    format="%2f"
                                                )
                                            },
                                            use_container_width = True,
                                            disabled=("Asset", "Allocation"),
                                            key="edits"
                                        )
                        # st.session_state.tflag = False
                        # print(st.session_state['tflag'])
        # Layout with two columns for ticker and allocation input
        with option2:
            tick, alloc = st.columns(2, gap='large')
            with tick:
                st.selectbox(
                    "Add your assets",
                    options=df['Ticker'],
                    key="asset_selection",
                    placeholder="Search",  
                    format_func=lambda x: "Search" if x is None else x 
                )

            # Display the number input for allocation only if an asset is selected
            with alloc:
                if st.session_state.asset_selection:
                    st.number_input(
                        'Add current allocation percent',
                        key='alloc_selection',
                        min_value=0.00,
                        max_value=100.00,
                        step=0.01,
                        format="%.2f",
                        on_change=reset_selectbox,  # Reset both asset and allocation after input
                        value=0.00 if st.session_state.alloc_selection is None else st.session_state.alloc_selection
                    )
                    # if st.session_state.alloc_selection:
                    #     print(st.session_state.assets_data)
                    #     st.session_state.tflag = True if st.session_state.tflag else tab_flag()
                    #     # print(st.session_state.assets_data.shape)
                else:
                    st.number_input(
                        'Add current allocation percent',
                        key='alloc_selection_disabled',
                        disabled=True
                    )
            # Display the final selected values (for reference)
            if st.session_state.asset and st.session_state.allocation:
                maxall = st.session_state.assets_data['Allocation'].max()
                maxlim = maxall + 5 - (maxall % 5)
                st.session_state.assets_data['Minimum Allocation'] = 0
                st.session_state.assets_data['Maximum Allocation'] = maxlim

                st.session_state.assets_data = st.data_editor(st.session_state.assets_data,
                                                    column_config={
                                                        "Minimum Allocation": st.column_config.NumberColumn(
                                                            "Minimum Allocation",
                                                            # help="",
                                                            min_value=0,
                                                            max_value=100,
                                                            step=0.01,
                                                            format="%2f",
                                                        ),
                                                        "Maximum Allocation": st.column_config.NumberColumn(
                                                            "Maximum Allocation",
                                                            # help="",
                                                            min_value=0,
                                                            max_value=100,
                                                            step=0.01,
                                                            format="%2f",
                                                        )
                                                    },
                                                    use_container_width = True,
                                                    disabled=("Asset", "Allocation"),
                                                    num_rows='dynamic',
                                                    # key="edits"
                                                )
                st.write(f"Total Allocation: {round(st.session_state.assets_data['Allocation'].sum(),2)}")
    
    if 'compare_port' not in st.session_state:
            st.session_state.compare_port = False

    st.button("Compare portfolio",on_click=call_mpt,key='comp')
    chart,bar = st.columns(2,gap='large')

    if 'compare_port' in st.session_state and st.session_state.compare_port is True:
        input_df = st.session_state.assets_data
        df = df[df['Ticker'].isin(input_df['Asset'])]
        df = df[df['Ticker'].isin(history['Ticker'])]
        input_df = input_df[input_df['Asset'].isin(history['Ticker'])]
        weights = input_df[input_df['Asset'].isin(df['Ticker'])]['Allocation'].to_numpy()
        exp_returns = df['Total Return'].to_numpy()
        rf_rate = 0.06
        try:
            cov = mpt.covariance_fc(history,df)
            curr_returns = mpt.portfolio_return(weights/100,exp_returns)
            curr_vol = mpt.portfolio_volatility(weights/100,cov)
        except Exception as e:
            st.error(f"Something didn't go right in CP please contact support with the error message! \n Error: {e}")
            st.stop()
        # curr_max = st.session_state.assets_data['Allocation'].max() # Static maximum -- deprecated
        # bound = curr_max + (5 - curr_max % 5)
        bound = list(zip(input_df['Minimum Allocation']/100, input_df['Maximum Allocation']/100))
        # with shar:
        fig,wgts = scatter_plot_custom(df,curr_returns,curr_vol,rf_rate,bound)
        with chart:
            st.header("Efficient Frontier")
            selected_points = plotly_events(fig, click_event=True, hover_event=False, key='select_port')

            if selected_points:
                try:
                    row_data = wgts.iloc[selected_points[0]['pointIndex'],:].to_list()
                except:
                    row_data = wgts.iloc[0,:].to_list()
                row_data = [round(x*100,2) for x in row_data]
                row_df = pd.DataFrame([row_data,weights]).T
                row_df.index = [x for x in input_df['Asset']]
                row_df.columns = ['Recommendation','Your Portfolio']
                if input_df['Allocation'].sum() < 100:
                    row_df.loc['Cash'] = [0,100 - input_df['Allocation'].sum()]
                with bar:
                    disp,dld = st.columns(2,gap='large)
                    with disp:
                        st.header("Allocation Comparison")
                    with dld:
                        st.download_button("Download as CSV",data = row_df.to_csv(),file_name=f'Returns_{selected_points[0]['y']}% Portfolio.csv',mime='text/csv')
                    st.write("Expected Return: ",selected_points[0]['y'],'\nVolatility: ',selected_points[0]['x'])
                    st.bar_chart(row_df,y_label='Allocations in %',stack=False)
