import os
from dash import Dash
import atexit
from src.layout.main_layout import create_layout
from src.services.ba_wrapper import initilize_bias_analyzer
from src.callbacks.cohort_callbacks import register_callbacks


bias_obj = initilize_bias_analyzer()

app = Dash(__name__)
app.title = 'BiasAnalyzer Web App'
server = app.server

atexit.register(bias_obj.cleanup)

app.layout = create_layout()

register_callbacks(app, bias_obj)

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=os.getenv('UI_PORT', 8855))
