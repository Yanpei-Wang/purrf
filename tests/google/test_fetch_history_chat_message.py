import unittest
from unittest.mock import Mock, patch
import logging
from io import StringIO
from google.fetch_history_chat_message import (
    fetch_messages_by_spaces_id,
    fetch_history_messages,
)
from google.constants import (
    NO_CLIENT_ERROR_MSG,
    CHAT_API_NAME,
    DEFAULT_PAGE_SIZE,
    FETCHING_MESSAGES_INFO_MSG,
    FETCHED_MESSAGES_INFO_MSG,
    DEFAULT_SPACE_TYPE,
    FETCHED_ALL_MESSAGES_INFO_MSG,
    SENDER_LDAP_NOT_FOUND_DEBUG_MSG,
    MESSAGE_TYPE_CREATE,
    STORED_MESSAGES_INFO_MSG,
)

TEST_SPACE_ID = "fhsdlfrp.dhiwqeq"
SPACE_ID_1 = "space1"
SPACE_ID_2 = "space2"
USER_ID_1 = "users/id1"
USER_ID_2 = "users/id2"
LDAP_1 = "ldap1"
LDAP_2 = "ldap2"
UNKNOWN_SENDER_ID = "unknown"

MESSAGE_TEXT_1 = "Hello"
MESSAGE_TEXT_2 = "Hi"
MOCK_MESSAGE_1 = {"sender": {"name": USER_ID_1}, "text": MESSAGE_TEXT_1}
MOCK_MESSAGE_2 = {"sender": {"name": USER_ID_2}, "text": MESSAGE_TEXT_2}
MOCK_MESSAGE_UNKNOWN = {"sender": {"name": "senderId/unknown"}, "text": MESSAGE_TEXT_1}

MOCK_SPACES = {SPACE_ID_1: "Space 1", SPACE_ID_2: "Space 2"}
MOCK_LDAP = {"id1": LDAP_1, "id2": LDAP_2}
MOCK_LDAP_PARTIAL = {"id1": LDAP_1}

MOCK_MESSAGES_RESPONSE = {
    "messages": [
        MOCK_MESSAGE_1,
        MOCK_MESSAGE_2,
    ],
    "nextPageToken": None,
}


class TestChatUtils(unittest.TestCase):
    def setUp(self):
        self.log_capture_string = StringIO()
        ch = logging.StreamHandler(self.log_capture_string)
        from tools.log.logger import setup_logger

        setup_logger()
        root_logger = logging.getLogger()
        ch.setFormatter(root_logger.handlers[0].formatter)
        logging.getLogger().addHandler(ch)
        logging.getLogger().setLevel(logging.DEBUG)

    def tearDown(self):
        logging.getLogger().handlers = []

    def test_fetch_messages_by_spaces_id_success(self):
        mock_client = Mock()
        mock_client.spaces.return_value.messages.return_value.list.return_value.execute.return_value = MOCK_MESSAGES_RESPONSE

        result = fetch_messages_by_spaces_id(mock_client, TEST_SPACE_ID)

        expected_result = MOCK_MESSAGES_RESPONSE["messages"]
        self.assertEqual(result, expected_result)
        mock_client.spaces.return_value.messages.return_value.list.assert_called_once_with(
            parent=f"spaces/{TEST_SPACE_ID}", pageSize=DEFAULT_PAGE_SIZE, pageToken=None
        )
        log_output = self.log_capture_string.getvalue()
        self.assertIn(
            FETCHING_MESSAGES_INFO_MSG.format(space_id=TEST_SPACE_ID), log_output
        )
        self.assertIn(
            FETCHED_MESSAGES_INFO_MSG.format(count=2, space_id=TEST_SPACE_ID),
            log_output,
        )
        self.assertNotIn(
            NO_CLIENT_ERROR_MSG.format(client_name=CHAT_API_NAME), log_output
        )

    def test_fetch_messages_by_spaces_id_invalid_client(self):
        mock_client = None
        with self.assertRaises(ValueError) as context:
            fetch_messages_by_spaces_id(mock_client, TEST_SPACE_ID)
        self.assertEqual(
            str(context.exception),
            NO_CLIENT_ERROR_MSG.format(client_name=CHAT_API_NAME),
        )

    @patch("google.fetch_history_chat_message.store_messages")
    @patch("google.fetch_history_chat_message.list_directory_all_people_ldap")
    @patch("google.fetch_history_chat_message.fetch_messages_by_spaces_id")
    @patch("google.fetch_history_chat_message.get_chat_spaces")
    @patch("google.authentication_utils.GoogleClientFactory.create_people_client")
    @patch("google.authentication_utils.GoogleClientFactory.create_chat_client")
    def test_fetch_history_messages_success(
        self,
        mock_create_chat_client,
        mock_create_people_client,
        mock_get_spaces,
        mock_fetch_messages,
        mock_list_ldap,
        mock_store_messages,
    ):
        mock_chat_client = Mock()
        mock_create_chat_client.return_value = mock_chat_client
        mock_people_client = Mock()
        mock_create_people_client.return_value = mock_people_client

        mock_get_spaces.return_value = MOCK_SPACES
        mock_fetch_messages.side_effect = [[MOCK_MESSAGE_1], [MOCK_MESSAGE_2]]
        mock_list_ldap.return_value = MOCK_LDAP
        mock_store_messages.return_value = None

        fetch_history_messages()

        mock_create_chat_client.assert_called_once()
        mock_create_people_client.assert_called_once()
        mock_get_spaces.assert_called_once_with(
            mock_chat_client, DEFAULT_SPACE_TYPE, DEFAULT_PAGE_SIZE
        )
        mock_fetch_messages.assert_any_call(mock_chat_client, SPACE_ID_1)
        mock_fetch_messages.assert_any_call(mock_chat_client, SPACE_ID_2)
        self.assertEqual(mock_fetch_messages.call_count, 2)
        mock_list_ldap.assert_called_once_with(mock_people_client)
        mock_store_messages.assert_any_call(LDAP_1, MOCK_MESSAGE_1, MESSAGE_TYPE_CREATE)
        mock_store_messages.assert_any_call(LDAP_2, MOCK_MESSAGE_2, MESSAGE_TYPE_CREATE)
        self.assertEqual(mock_store_messages.call_count, 2)

        log_output = self.log_capture_string.getvalue()
        self.assertIn(
            FETCHED_MESSAGES_INFO_MSG.format(count=1, space_id=SPACE_ID_1), log_output
        )
        self.assertIn(
            FETCHED_MESSAGES_INFO_MSG.format(count=1, space_id=SPACE_ID_2), log_output
        )
        self.assertIn(FETCHED_ALL_MESSAGES_INFO_MSG.format(count=2), log_output)
        self.assertIn(
            STORED_MESSAGES_INFO_MSG.format(stored_count=2, total_count=2), log_output
        )
        self.assertNotIn(
            SENDER_LDAP_NOT_FOUND_DEBUG_MSG.format(
                sender_id=USER_ID_1, message=MOCK_MESSAGE_1
            ),
            log_output,
        )

    @patch("google.fetch_history_chat_message.store_messages")
    @patch("google.fetch_history_chat_message.list_directory_all_people_ldap")
    @patch("google.fetch_history_chat_message.fetch_messages_by_spaces_id")
    @patch("google.fetch_history_chat_message.get_chat_spaces")
    @patch("google.authentication_utils.GoogleClientFactory.create_people_client")
    @patch("google.authentication_utils.GoogleClientFactory.create_chat_client")
    def test_fetch_history_messages_with_unknown_sender(
        self,
        mock_create_chat_client,
        mock_create_people_client,
        mock_get_spaces,
        mock_fetch_messages,
        mock_list_ldap,
        mock_store_messages,
    ):
        mock_chat_client = Mock()
        mock_create_chat_client.return_value = mock_chat_client
        mock_people_client = Mock()
        mock_create_people_client.return_value = mock_people_client

        mock_get_spaces.return_value = MOCK_SPACES
        mock_fetch_messages.side_effect = [
            [MOCK_MESSAGE_UNKNOWN],
            [MOCK_MESSAGE_UNKNOWN],
        ]
        mock_list_ldap.return_value = MOCK_LDAP_PARTIAL
        mock_store_messages.return_value = None

        fetch_history_messages()

        mock_create_chat_client.assert_called_once()
        mock_create_people_client.assert_called_once()
        mock_get_spaces.assert_called_once_with(
            mock_chat_client, DEFAULT_SPACE_TYPE, DEFAULT_PAGE_SIZE
        )
        mock_fetch_messages.assert_any_call(mock_chat_client, SPACE_ID_1)
        mock_fetch_messages.assert_any_call(mock_chat_client, SPACE_ID_2)
        self.assertEqual(mock_fetch_messages.call_count, 2)
        mock_list_ldap.assert_called_once_with(mock_people_client)
        mock_store_messages.assert_not_called()

        log_output = self.log_capture_string.getvalue()
        self.assertIn(
            SENDER_LDAP_NOT_FOUND_DEBUG_MSG.format(
                sender_id=UNKNOWN_SENDER_ID, message=MOCK_MESSAGE_UNKNOWN
            ),
            log_output,
        )
        self.assertIn(
            STORED_MESSAGES_INFO_MSG.format(stored_count=0, total_count=2), log_output
        )


if __name__ == "__main__":
    unittest.main()
