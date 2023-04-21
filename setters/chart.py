import plotly.graph_objs as go

def chart(stored_symbol, stock_data, chart_type_value, time_frame_value):
    data = None
    title = None

    if chart_type_value == 'candlestick':
        data = [go.Candlestick(
            x=stock_data['date'],
            open=stock_data['1. open'],
            high=stock_data['2. high'],
            low=stock_data['3. low'],
            close=stock_data['4. close']
        )]
        title = f"{stored_symbol.upper()} - {time_frame_value} Prices"
    elif chart_type_value == 'line':
        data = [go.Scatter(
            x=stock_data['date'],
            y=stock_data['4. close'],
            mode='lines'
        )]
        title = f"{stored_symbol.upper()} - {time_frame_value} Prices"
    
    return data, title