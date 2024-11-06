import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
from scipy.optimize import minimize

history = pd.read_csv('bayesian_forecast.csv')
def covariance_fc(history,df):
    mat = history[history['Ticker'].isin(df['Ticker'])]
    mat = mat.T
    mat.columns = mat.iloc[0,:]
    mat = mat.iloc[1:,:]
    imputer = KNNImputer(n_neighbors=10)
    mat_filled = imputer.fit_transform(mat)
    pctchg = mat_filled/100
    pctchg_vol = pctchg.std()
    arith_mean = np.mean(pctchg,axis=0)
    pctchg_centered = pctchg - arith_mean
    V = pctchg_centered.T.dot(pctchg_centered)/pctchg.shape[0]  # historic covariance matrix
    gamma = np.asarray(df['IV'])
    factor = gamma/pctchg_vol # scaling factor for diagonal scaling method
    D = np.diag(factor)  # diagonal scaling matrix
    try:
        forecasted_cov = D @ V @ D # forecasted covariance
        return forecasted_cov
    except:
        return None
    

# Portfolio statistics functions
def portfolio_volatility(weights, cov_matrix):
    return np.dot(weights.T, np.dot(cov_matrix, weights))

# Define the constraint: portfolio return should be equal to the target return
def portfolio_return(weights, expected_returns):
    return np.dot(weights, expected_returns)

# Define the function to minimize the negative Sharpe ratio
def negative_sharpe_ratio(weights, expected_returns, cov_matrix, risk_free_rate):
    port_return = portfolio_return(weights, expected_returns)
    port_variance = portfolio_volatility(weights, cov_matrix)
    return -(port_return - risk_free_rate) / np.sqrt(port_variance)

# Define the constraint function for the target return
def return_constraint(weights, expected_returns, target_return):
    return portfolio_return(weights, expected_returns) - target_return

def mpt(mat,expected_returns,bound):
    n_assets = mat.shape[0]
    if type(bound) == list:
        bounds = bound
    else:
        bounds = [(0, bound) for _ in range(n_assets)]
    risk_free_rate = 0.06
    opt_weights,opt_returns,opt_volatility,opt_sharpe_ratio = [],[],[],[]
    # Optimize portfolio
    expected_returns = expected_returns/100
    min_port = min(expected_returns)
    max_port = max(expected_returns)
    portfolio_returns = np.arange(min_port,max_port,(max_port-min_port)/20)
    for ret in portfolio_returns:
        # Portfolio weights
        initial_weights = np.ones(n_assets) / n_assets
        # initial_weights = initial_weights / np.sum(initial_weights)
        constraints = ({
                            'type': 'eq',
                            'fun': lambda weights: np.sum(weights) - 1
                        }, {
                            'type': 'eq',
                            'fun': lambda weights: return_constraint(weights, expected_returns, ret)
                        })
        result = minimize(
            fun=negative_sharpe_ratio,
            x0=initial_weights,
            args=(expected_returns, mat, risk_free_rate),
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        # Optimal weights
        if result.success:
            weights = result.x
            returns = portfolio_return(weights, expected_returns)
            volatility = portfolio_volatility(weights, mat)
            sharpe_ratio = -result.fun

            opt_weights.append(weights)
            opt_returns.append(returns)
            opt_volatility.append(volatility)
            opt_sharpe_ratio.append(sharpe_ratio)

    return opt_returns,opt_volatility,opt_weights

def generate_portfolio(df,bound=10):
    df = df[df['Ticker'].isin(history.Ticker)]
    mat = covariance_fc(history,df)
    returns,volatility,weights = mpt(mat,df['Total Return'],bound)
    volatility = [round(x,2) for x in volatility]
    returns = [round(y*100,2) for y in returns]
    weights = pd.DataFrame(weights,columns=df['Ticker'])
    return(returns,volatility,weights)
