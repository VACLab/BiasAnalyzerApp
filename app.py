import copy
import os
import base64
import tempfile
import uuid
import datetime
import pandas as pd
import atexit
from dash import Dash, dcc, html, Input, Output, State, dash_table
from dash.exceptions import PreventUpdate
import plotly.express as px
from src.utils import initilize_bias_analyzer


bias_obj = initilize_bias_analyzer()

app = Dash(__name__)
app.title = 'BiasAnalyzer Web App'
server = app.server

atexit.register(bias_obj.cleanup)

app.layout = html.Div([
    html.H1("Bias Analyzer"),

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
])

@app.callback(
    Output('upload-feedback', 'children'),
    Input('upload-cohort', 'filename')
)
def update_upload_feedback(filename):
    if filename:
        return f"✅ Uploaded file: {filename}"
    return ""


@app.callback(
    [Output('output-summary', 'children'),
     Output('output-table', 'children'),
     Output('form-feedback', 'children'),
     Output('cohort-duration-plot', 'children')],
    [Input('submit-button', 'n_clicks')],
    [State('cohort-name', 'value'),
     State('cohort-description', 'value'),
     State('upload-cohort', 'contents'),
     State('upload-cohort', 'filename')]
)
def handle_cohort_submission(n_clicks, name, description, contents, filename):
  if n_clicks == 0:
    raise PreventUpdate

  # === Validate required fields ===
  if not name or not description:
    return "", "", "❗ Please enter both cohort name and description.", ""

  if not contents or not filename:
    return "", "", "❗ Please upload a cohort YAML file.", ""

  try:
    # Decode and parse YAML
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    # Save to temp file
    unique_id = uuid.uuid4().hex
    tmp_filename = f"cohort_{unique_id}.yaml"
    tmp_path = os.path.join(tempfile.gettempdir(), tmp_filename)
    with open(tmp_path, 'wb') as f:
      f.write(decoded)

    # Create cohort using global `bias` object
    cohort_obj = bias_obj.create_cohort(name, description, tmp_path, f"user_{unique_id}")
    summary_data = cohort_obj.get_stats()
    summary_table = dash_table.DataTable(
      data=[{"Metric": k.replace("_", " ").title(), "Value": v} for k, v in summary_data[0].items()],
      columns=[{"name": "Metric", "id": "Metric"}, {"name": "Value", "id": "Value"}],
      style_cell={"textAlign": "left"},
    )

    patients = cohort_obj.data
    display_patients = copy.deepcopy(patients[:10])
    # Format dates as strings for readability
    for patient in display_patients:
      for k, v in patient.items():
        if isinstance(v, (pd.Timestamp, datetime.date)):
          patient[k] = v.isoformat()

    patients_table = dash_table.DataTable(
      data=display_patients,
      columns=[{"name": k.replace("_", " ").title(), "id": k} for k in display_patients[0].keys()],
      style_table={"overflowX": "auto"},
      page_size=10,
    )

    # Duration histogram plot
    durations_days = [
      (p['cohort_end_date'] - p['cohort_start_date']).days
      for p in patients
      if p['cohort_end_date'] and p['cohort_start_date']
    ]

    duration_fig = px.histogram(
      x=durations_days,
      nbins=30,
      labels={"x": "Cohort Duration (days)", "y": "Patient Count"},
      title="Distribution of Cohort Duration",
      template="plotly_white"
    )

    duration_plot = dcc.Graph(figure=duration_fig)

    return (
      html.Div([
        html.H3("Cohort Summary"),
        summary_table,
      ]),
      html.Div([
        html.H3("First 10 Patients in Cohort"),
        patients_table,
      ]),
      "",
      html.Div([
        html.H3("Cohort Duration Histogram"),
        duration_plot
      ])
    )

  except Exception as e:
    return "", "", f"❗ Error creating cohort: {str(e)}", ""

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=os.getenv('UI_PORT', 8855))
