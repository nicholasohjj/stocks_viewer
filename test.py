import dash
import dash_core_components as dcc
import dash_html_components as html

# Create a Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div(children=[
    html.H1(children='Dynamic HTML Text'),
    dcc.Input(id='input-box', type='text', value='Hello, Dash!'),
    html.Div(id='output-container', children=[
        html.P(id='output-text', children='Output will be displayed here')
    ])
])

# Define callback to update the output text
@app.callback(
    dash.dependencies.Output('output-text', 'children'),
    [dash.dependencies.Input('input-box', 'value')]
)
def update_output_text(input_value):
    # Use the input value to generate the HTML text
    html_text = html.B(input_value)  # Make the text bold
    return html_text

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
