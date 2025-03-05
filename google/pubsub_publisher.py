# Implement those function in this file:
# create_pubsub_topic(publisher_client, project_id, topic_id)
# create_workspaces_subscriptions(project_id, topic_id, client, space_id, event_types)
# create_subscription(project_id, topic_id, subscription_id)
# subscribe_chat(topic_id, subscription_id, space_id)


from tools.log.logger import setup_logger
from google.authentication_utils import GoogleClientFactory
from google.cloud.pubsub_v1.types import Subscription
import logging

setup_logger()


def create_subscription(project_id, topic_id, subscription_id):
    """
    Creates a Google Cloud Pub/Sub subscription for a given topic with no expiration.

    Args:
        project_id (str): Google Cloud Project ID.
        topic_id (str): The Pub/Sub topic ID to subscribe to.
        subscription_id (str): The subscription ID to be created.

    Returns:
        str: The name of the created subscription.

    Raises:
        ValueError: if project_id or topic_id or subscription_id is empty.
    """

    if not project_id or not topic_id or not subscription_id:
        raise ValueError(
            "project_id and topic_id and subscription_id must be provided."
        )

    subscriber = GoogleClientFactory().create_subscriber_client()
    topic_path = subscriber.topic_path(project_id, topic_id)
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    subscription = Subscription(
        name=subscription_path, topic=topic_path, expiration_policy=None
    )

    subscriber.create_subscription(
        request={"name": subscription.name, "topic": subscription.topic}
    )

    logging.info(f"Subscription created: {subscription_path}")
    return subscription_path

def create_pubsub_topic(publisher_client, project_id, topic_id):
    """
    Creates a Pub/Sub topic in the specified project.

    Args:
        publisher_client (google.cloud.pubsub_v1.PublisherClient): The Publisher client instance.
        project_id (str): The ID of your Google Cloud project.
        topic_id (str): The ID of the topic to create.

    Returns:
        google.cloud.pubsub_v1.types.Topic: The created Topic object.

    Raises:
        ValueError: If project_id or topic_id is empty.
    """

    if not publisher_client or not project_id or not topic_id:
        raise ValueError("Publisher_client, project_id and topic_id must be provided.")
    topic_path = publisher_client.topic_path(project_id, topic_id)
    topic = publisher_client.create_topic(name=topic_path)
    logging.info(f"Topic created: {topic_path}")
    return topic