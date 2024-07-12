from waitress import serve
from dashboard import create_app
from dashboard_websocket import create_socket
import threading
from dashboard.db import init_db
# python -c "from server import run_server; run_server()"

def run_server():
    dashboard = create_app()
    create_socket()
    # serve(dashboard, host='0.0.0.0', port=5000)
    # dashboard.run(host='0.0.0.0', port=5000)
    # t1 = threading.Thread(target=lambda: serve(dashboard, host='0.0.0.0', port=5000))
    t1 = threading.Thread(target=lambda: dashboard.run(host='0.0.0.0', port=5000))
    t1.start()
    print("DASHBOARD: Started")

def initialize_database():
    dashboard = create_app()
    with dashboard.app_context():
        init_db()