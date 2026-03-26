from dash import html, dcc

def create_layout():
    return html.Div([
        html.H1("Bias Analyzer"),
        html.Div(id="status-text"),
        html.Div(id="page-load", style={"display": "none"}),
        html.Label("Cohort Name"),
        dcc.Input(id='cohort-name', type='text', placeholder='Enter cohort name', value=''),

        html.Label("Cohort Description"),
        dcc.Textarea(id='cohort-description', placeholder='Enter cohort description', value=''),

        html.Label("Upload cohort creation specification YAML file"),
        dcc.Upload(
          id='upload-cohort',
          children=html.Div(
            'Drag and drop or click to upload a YAML file',
            className='upload-box-text'
          ),
          className='upload-box',
          accept=".yaml,.yml",
          multiple=False
        ),
        html.Div(id='upload-feedback', className='upload-feedback'),
        html.Div(id='form-feedback'),
        html.Button("Create Cohort", id="submit-button", n_clicks=0),
        html.Div(id='output-summary'),
        html.Div(id='output-table'),
        html.Div(id='cohort-duration-plot'),
        dcc.Store(id="yaml-file-path", storage_type="session")
    ])
