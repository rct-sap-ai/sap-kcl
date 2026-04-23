import unittest
from unittest.mock import Mock, patch

import requests

from auto_sap.classes.auto_code_api_classes import AutoCodeAPI, TrialMetadata


class AutoCodeAPITests(unittest.TestCase):
    def setUp(self):
        self.api = AutoCodeAPI(token="test-token", dev=False)

    @staticmethod
    def _metadata_payload(has_protocol=True):
        return {
            "id": 12,
            "acronym": "ABC",
            "title": "Example Trial",
            "has_protocol": has_protocol,
            "protocol_filename": "study-protocol.pdf" if has_protocol else None,
            "protocol_download_url": "http://backend/trial/12/protocol/" if has_protocol else None,
        }

    @patch("auto_sap.classes.auto_code_api_classes.requests.get")
    def test_get_trial_metadata_parses_protocol_fields(self, mock_get):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = self._metadata_payload()
        mock_get.return_value = response

        trial_metadata = self.api.get_trial_metadata(12)

        self.assertIsInstance(trial_metadata, TrialMetadata)
        self.assertEqual(trial_metadata.id, 12)
        self.assertEqual(trial_metadata.acronym, "ABC")
        self.assertEqual(trial_metadata.title, "Example Trial")
        self.assertTrue(trial_metadata.has_protocol)
        self.assertEqual(trial_metadata.protocol_filename, "study-protocol.pdf")
        self.assertEqual(trial_metadata.protocol_download_url, "http://backend/trial/12/protocol/")

    @patch("auto_sap.classes.auto_code_api_classes.requests.get")
    def test_get_protocol_file_downloads_binary_content(self, mock_get):
        metadata_response = Mock()
        metadata_response.raise_for_status.return_value = None
        metadata_response.json.return_value = self._metadata_payload()

        binary_response = Mock()
        binary_response.raise_for_status.return_value = None
        binary_response.content = b"%PDF-1.4 fake"

        mock_get.side_effect = [
            metadata_response,
            binary_response,
            metadata_response,
            binary_response,
        ]

        protocol_bytes = self.api.get_protocol_bytes(12)
        protocol_file = self.api.get_protocol_file(12)

        self.assertEqual(protocol_bytes, b"%PDF-1.4 fake")
        self.assertEqual(protocol_file, (b"%PDF-1.4 fake", "study-protocol.pdf"))
        self.assertEqual(mock_get.call_count, 4)
        self.assertEqual(mock_get.call_args_list[1].kwargs["headers"]["Authorization"], "Token test-token")
        self.assertEqual(mock_get.call_args_list[1].args[0], "https://www.statsplan.com/api/trial/12/protocol/")
        self.assertEqual(mock_get.call_args_list[3].args[0], "https://www.statsplan.com/api/trial/12/protocol/")

    @patch("auto_sap.classes.auto_code_api_classes.requests.get")
    def test_get_protocol_when_missing_returns_none(self, mock_get):
        metadata_response = Mock()
        metadata_response.raise_for_status.return_value = None
        metadata_response.json.return_value = self._metadata_payload(has_protocol=False)
        mock_get.return_value = metadata_response

        self.assertIsNone(self.api.get_protocol_bytes(12))
        self.assertEqual(self.api.get_protocol_file(12), (None, None))
        self.assertEqual(mock_get.call_count, 2)

    @patch("auto_sap.classes.auto_code_api_classes.requests.get")
    def test_get_protocol_download_propagates_http_errors(self, mock_get):
        metadata_response = Mock()
        metadata_response.raise_for_status.return_value = None
        metadata_response.json.return_value = self._metadata_payload()

        binary_response = Mock()
        binary_response.raise_for_status.side_effect = requests.HTTPError("download failed")

        mock_get.side_effect = [metadata_response, binary_response]

        with self.assertRaises(requests.HTTPError):
            self.api.get_protocol_bytes(12)


if __name__ == "__main__":
    unittest.main()
