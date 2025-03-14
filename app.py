"""google chat service"""

from flask import Flask, jsonify, request
from google.fetch_history_chat_message import (
    fetch_history_messages,
    get_all_chat_spaces,
)
from google.pubsub_publisher import subscribe_chat
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


@app.route("/api/chat/spaces/subscribe")
def subscribe():
    """API endpoint to retrieve a list of Google Chat spaces."""
    project_id = request.args.get("project_id")
    space_id = request.args.get("space_id")
    subscription_id = request.args.get("subscription_id")
    topic_id = request.args.get("topic_id")
    data = subscribe_chat(project_id, space_id, subscription_id, topic_id)
    return jsonify({"spaces": data}), http.client.OK


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
