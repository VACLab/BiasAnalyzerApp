# all cohort-related callback functions
import copy
from dash import Input, Output, State, dcc, html, dash_table, no_update
from flask import session
import base64, uuid, os, tempfile, pandas as pd
from datetime import date
from dash.exceptions import PreventUpdate
import plotly.express as px


# This will be called once per user session
def get_user_session_id():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return session['user_id']


def register_callbacks(app, bias_obj):
    if bias_obj is None:
        raise ValueError("bias_obj must be provided to register_callbacks()")

    @app.callback(
        Output('yaml-file-path', 'data'),
        Output('upload-feedback', 'children'),
        Input('upload-cohort', 'contents'),
        State('upload-cohort', 'filename'),
        prevent_initial_call=True
    )
    def handle_upload(contents, filename):
        if contents is None or filename is None:
            raise PreventUpdate

        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            yaml_text = decoded.decode('utf-8')

            unique_id = uuid.uuid4().hex
            tmp_filename = f"cohort_{unique_id}.yaml"
            tmp_path = os.path.join(tempfile.gettempdir(), tmp_filename)

            with open(tmp_path, 'w', encoding='utf-8') as f:
                f.write(yaml_text)

            return tmp_path, f"✅ Uploaded file: {filename}"
        except Exception as e:
            return no_update, f"❗ Error uploading file: {str(e)}"

    @app.callback(
        [Output('output-summary', 'children'),
         Output('output-table', 'children'),
         Output('form-feedback', 'children'),
         Output('cohort-duration-plot', 'children')],
        [Input('submit-button', 'n_clicks')],
        [State('cohort-name', 'value'),
         State('cohort-description', 'value'),
         State('yaml-file-path', 'data')],
        prevent_initial_call=True
    )
    def handle_cohort_submission(n_clicks, name, description, tmp_path):
        if n_clicks == 0:
            raise PreventUpdate

        if not name or not description:
            return "", "", "❗ Please input both cohort name and description.", ""

        if not tmp_path or not os.path.exists(tmp_path):
            return "", "", "❗ A cohort creation YAML file is not uploaded or not available", ""

        try:
            # Save to temp file
            user_id = get_user_session_id()
            # Create cohort
            cohort_obj = bias_obj.create_cohort(name, description, tmp_path, user_id)

            common_style_cell = {"textAlign": "left", "padding": "5px"}
            summary_data = cohort_obj.get_stats()
            summary_table = dash_table.DataTable(
                data=[{"Metric": k.replace("_", " ").title(), "Value": v} for k, v in summary_data[0].items()],
                columns=[{"name": "Metric", "id": "Metric"}, {"name": "Value", "id": "Value"}],
                style_cell=common_style_cell,
            )

            patients = cohort_obj.data
            display_patients = copy.deepcopy(patients[:10])
            # Format dates as strings for readability
            for patient in display_patients:
                for k, v in patient.items():
                    if isinstance(v, (pd.Timestamp, date)):
                        patient[k] = v.isoformat()

            patients_table = dash_table.DataTable(
                data=display_patients,
                columns=[{"name": k.replace("_", " ").title(), "id": k} for k in display_patients[0].keys()],
                style_table={"overflowX": "auto"},
                style_cell=common_style_cell,
                page_size=10,
            )

            # Duration histogram plot
            durations_days = [
                (p['cohort_end_date'] - p['cohort_start_date']).days
                for p in patients
                if p['cohort_start_date'] and p['cohort_end_date']
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
