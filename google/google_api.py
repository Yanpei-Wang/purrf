"""google chat service"""

from flask import jsonify, Blueprint, request
from google.fetch_history_chat_message import fetch_history_messages
from google.pubsub_publisher import subscribe_chat
import http.client
from concurrent.futures import ThreadPoolExecutor

google_bp = Blueprint("google", __name__)

executor = ThreadPoolExecutor(max_workers=5)


@google_bp.route("/api/chat/spaces/messages")
def history_messages():
    """API endpoint to trigger the fetching of messages for all SPACE type chat spaces and store them in Redis asynchronously."""

    executor.submit(fetch_history_messages)
    return jsonify({
        "message": "Message retrieval triggered asynchronously."
    }), http.client.ACCEPTED


@google_bp.route("/api/chat/spaces/subscribe")
def subscribe():
    """API endpoint to retrieve a list of Google Chat spaces."""
    project_id = request.args.get("project_id")
    space_id = request.args.get("space_id")
    subscription_id = request.args.get("subscription_id")
    topic_id = request.args.get("topic_id")
    data = subscribe_chat(project_id, space_id, subscription_id, topic_id)
    return jsonify({"spaces": data}), http.client.OK
