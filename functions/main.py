from firebase_functions import https_fn
from firebase_admin import initialize_app
from telegram_bot_api import app

initialize_app()


@https_fn.on_request()
def api(request: https_fn.Request) -> https_fn.Response:
    with app.request_context(request.environ):
        return app.full_dispatch_request()

