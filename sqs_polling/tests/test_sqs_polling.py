import unittest
from unittest.mock import MagicMock, patch

from ..sqs_polling import _receive, _execute


class TestSqsPolling(unittest.TestCase):
    def _get_queue_url(self):
        return "https://sqs.ap-northeast-1.amazonaws.com/XXXXXXXXXXXX/your-sqs"

    def _get_receipt_handle(self, i):
        return "ReceiptHandle_{}".format(i)

    def _get_body(self, i):
        return "Body_{}".format(i)

    def _get_responses(self, message_num):
        response = {
            "ResponseMetadata": {
                "RetryAttempts": 0,
                "HTTPHeaders": {
                    "content-type": "text/xml",
                    "content-length": "860",
                    "x-amzn-requestid": "66222d85-7321-7aa2-b21a-7ba1eb393a4a",
                    "date": "Sat, 19 Oct 2019 04:49:28 GMT"
                },
                "RequestId": "d7aa8408-0fa8-5a29-8538-d22c900749c1",
                "HTTPStatusCode": 200
            }
        }

        if message_num > 0:
            messages = []

            for i in range(message_num):
                messages.append({
                    "ReceiptHandle": self._get_receipt_handle(i),
                    "MD5OfBody": "1db65a6a0a818fd39655b95e34ada11d",
                    "MessageId": "58da63b0-426b-4fda-9b47-64017fd441dd",
                    "Body": self._get_body(i),
                })

            response["Messages"] = messages

        return response

    def test_receive_no_messages(self):
        sqs_mock = MagicMock()
        sqs_mock.receive_message.return_value = self._get_responses(0)

        ret = _receive(sqs_mock, "", 300, 1)

        assert ret == []

    def test_receive_1_message(self):
        sqs_mock = MagicMock()
        sqs_mock.receive_message.return_value = self._get_responses(1)

        ret = _receive(sqs_mock, "", 300, 1)

        assert len(ret) == 1
        assert ret[0]["Body"] == self._get_body(0)

    def test_receive_2_messages(self):
        sqs_mock = MagicMock()
        sqs_mock.receive_message.return_value = self._get_responses(2)

        ret = _receive(sqs_mock, "", 300, 2)

        assert len(ret) == 2
        assert ret[1]["Body"] == self._get_body(1)

    def test_execute_delete(self):
        sqs_mock = MagicMock()
        callback_mock = MagicMock(return_value=True)

        with patch("boto3.client", return_value=sqs_mock) as _:
            _execute({}, self._get_queue_url(),
                     callback_mock, None, self._get_responses(1)["Messages"], True)

        callback_mock.assert_called_once_with(self._get_body(0))

        sqs_mock.delete_message.assert_called_once_with(
            QueueUrl=self._get_queue_url(), ReceiptHandle=self._get_receipt_handle(0)
        )

    def test_execute_not_delete(self):
        sqs_mock = MagicMock()
        callback_mock = MagicMock(return_value=False)

        with patch("boto3.client", return_value=sqs_mock) as _:
            _execute(sqs_mock, self._get_queue_url(),
                     callback_mock, None, self._get_responses(1)["Messages"], True)

        callback_mock.assert_called_once_with(self._get_body(0))

        sqs_mock.delete_message.assert_not_called()

    def test_execute_with_args(self):
        sqs_mock = MagicMock()
        callback_mock = MagicMock(return_value=True)

        with patch("boto3.client", return_value=sqs_mock) as _:
            _execute(sqs_mock, self._get_queue_url(), callback_mock,
                     (1, "2"), self._get_responses(1)["Messages"], True)

        callback_mock.assert_called_once_with(self._get_body(0), *(1, "2"))

    def test_execute_with_kwargs(self):
        sqs_mock = MagicMock()
        callback_mock = MagicMock(return_value=True)

        with patch("boto3.client", return_value=sqs_mock) as _:
            _execute(sqs_mock, self._get_queue_url(), callback_mock,
                     {"key1": 1, "key2": "2"}, self._get_responses(1)["Messages"], True)

        callback_mock.assert_called_once_with(self._get_body(0), **{"key1": 1, "key2": "2"})

    def test_execute_with_whole(self):
        sqs_mock = MagicMock()
        callback_mock = MagicMock(return_value=True)

        with patch("boto3.client", return_value=sqs_mock) as _:
            _execute(sqs_mock, self._get_queue_url(), callback_mock,
                     None, self._get_responses(1)["Messages"], False)

        callback_mock.assert_called_once_with(self._get_responses(1)["Messages"][0])

    def test_execute_callback_returns_not_bool(self):
        sqs_mock = MagicMock()
        callback_mock = MagicMock(return_value=None)

        try:
            with patch("boto3.client", return_value=sqs_mock) as _:
                _execute(sqs_mock, self._get_queue_url(), callback_mock,
                         None, self._get_responses(1)["Messages"], True)
        except TypeError:
            assert True
        except:
            assert False
        else:
            assert False
