import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Create a Dash app
app = dash.Dash(__name__)

# Define the text content using Markdown syntax
text_content = '''
## Dash Dashboard Example

This is an example of a Dash dashboard with custom text content.

### Heading 3

- Bullet point 1
- Bullet point 2
- Bullet point 3

**Bold text** and *italic text* can also be used.

> Blockquote can be used for important information.

'''

# Define the layout of the Dash app using CSS flexbox
app.layout = html.Div(
    style={'display': 'flex', 'flexDirection': 'column', 'height': '100vh'},
    children=[
        html.Header(
            style={'flex': '0 0 auto', 'backgroundColor': 'lightgray', 'padding': '10px'},
            children=[
                html.H1('My Dash Dashboard', style={'margin': '0'})
            ]
        ),
        html.Div(
            style={'flex': '1 1 auto', 'padding': '20px', 'overflowY': 'auto'},
            children=[
                dcc.Markdown(children=text_content)  # Use dcc.Markdown component to render the text content
            ]
        ),
        html.Footer(
            style={'flex': '0 0 auto', 'backgroundColor': 'lightgray', 'padding': '10px', 'marginTop': 'auto'},
            children=[
                html.P('Footer text', style={'margin': '0'})
            ]
        )
    ]
)

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
