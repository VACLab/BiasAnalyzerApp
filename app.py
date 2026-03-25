import os
from dash import Dash
import atexit
from src.layout.main_layout import create_layout
from src.services.ba_wrapper import initialize_bias_analyzer
from src.callbacks.cohort_callbacks import register_callbacks


bias_obj = initialize_bias_analyzer()

app = Dash(__name__)
app.title = 'BiasAnalyzer Web App'
server = app.server
server.secret_key = os.getenv('SESSION_SECRET_KEY', 'fallback-insecure-dev-key')

debug_flag = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')
if not debug_flag:
  server.config.update(
      SESSION_COOKIE_SECURE=True,     # using HTTPS
      SESSION_COOKIE_HTTPONLY=True,   # prevent JS access
      SESSION_COOKIE_SAMESITE='Lax'   # reasonable CSRF protection
  )

atexit.register(bias_obj.cleanup)

app.layout = create_layout()

register_callbacks(app, bias_obj)

if __name__ == '__main__':
  app.run(debug=debug_flag, host='0.0.0.0', port=os.getenv('UI_PORT', 8855))
