"""google chat service"""

from flask import Flask, jsonify
from google.fetch_history_chat_message import (
    fetch_history_messages,
    get_all_chat_spaces,
)
import http.client
from tools.global_handle_exception.exception_handler import register_error_handlers
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
register_error_handlers(app)
executor = ThreadPoolExecutor(max_workers=5)


@app.route("/api/chat/spaces/messages")
def history_messages():
    """API endpoint to trigger the fetching of messages for all SPACE type chat spaces and store them in Redis asynchronously."""

    executor.submit(fetch_history_messages)
    return jsonify({
        "message": "Message retrieval triggered asynchronously."
    }), http.client.ACCEPTED


@app.route("/api/chat/spaces")
def spaces():
    """API endpoint to retrieve a list of Google Chat spaces."""

    spaces_data = get_all_chat_spaces()
    return jsonify({"spaces": spaces_data}), http.client.OK


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
