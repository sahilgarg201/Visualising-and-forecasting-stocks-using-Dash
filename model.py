def predict(stock,days_n):
    from model import predict
    import pandas as pd
    from pandas.io.formats import style
    from pandas_datareader import data as pdr
    from datetime import datetime as date
    from datetime import timedelta
    import dash
    import dash_core_components as dcc
    import dash_html_components as html
    from dash.dependencies import Input, Output, State
    import plotly.graph_objs as go
    import plotly.express as px
    import yfinance as yf
    from dash.exceptions import PreventUpdate
    from sklearn.model_selection import GridSearchCV
    from sklearn.svm import SVR
    from sklearn.model_selection import train_test_split

    df = yf.download(stock, period='100d')
    df.reset_index(inplace=True)
    df['Day'] = df.index
    days = list()
    for i in range(len(df.Day)):
        days.append([i])

    X=days
    Y=df[['Close']]
    x_train, x_test, y_train, y_test = train_test_split(X, Y,test_size=0.1,shuffle=False)
    gsc = GridSearchCV(
        estimator=SVR(kernel='rbf'),
        param_grid={
            'C': [0.1, 1, 100, 1000],
            'epsilon': [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5, 10],
            'gamma': [0.0001, 0.001, 0.005, 0.1, 1, 3, 5]
        },
        cv=5, scoring='neg_mean_squared_error', verbose=0, n_jobs=-1)
    y_train = y_train.values.ravel()
    grid_result = gsc.fit(x_train, y_train)
    best_params = grid_result.best_params_
    best_svr = SVR(kernel='rbf', C=best_params["C"], epsilon=best_params["epsilon"], gamma=best_params["gamma"],
                   coef0=0.1, shrinking=True,
                   tol=0.001, cache_size=200, verbose=False, max_iter=-1)
    svr_rbf=best_svr
    svr_rbf=SVR(kernel='rbf',C=1e3,gamma=0.1)
    svr_rbf.fit(x_train,y_train)

    output_days = list()
    for i in range(1, days_n):
        output_days.append([i + x_test[-1][0]])

    dates = []
    current = date.today()
    for i in range(days_n):
        current += timedelta(days=1)
        dates.append(current)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates,y=svr_rbf.predict(output_days),mode='lines+markers',name='data'))
    fig.update_layout(title="Predicted Close Price of next " + str(days_n - 1) + " days",xaxis_title="Date",yaxis_title="Closed Price",legend_title="tips")
    return fig