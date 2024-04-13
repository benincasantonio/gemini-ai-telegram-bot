from firebase_functions import https_fn
from firebase_admin import initialize_app
from src.telegram_bot_api import app
from dotenv import load_dotenv

load_dotenv()

initialize_app()


@https_fn.on_request()
def api(request: https_fn.Request) -> https_fn.Response:
    with app.request_context(request.environ):
        return app.full_dispatch_request()

