import boto3
import asyncio
from typing import Callable, Union, Optional
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


def sqs_polling(queue_url: str, callback: Callable[..., bool], callback_args: Union[list, tuple, dict, None] = None,
                extract_body: bool = True, visibility_timeout: int = 300, interval_seconds: float = 1.0,
                max_workers: int = 1, process_worker: bool = False, aws_profile_dict: Optional[dict] = None):
    """
    Polls AWS SQS and executes your callback.

    Parameters
    ----------
    queue_url : str
        SQS URL (ex. https://sqs.your-region.amazonaws.com/XXXXXXXXXXXX/your-sqs)
    callback : function
        Function to process each message.
        The first argument is str type or dict type, and the received message is passed.
        The second and subsequent arguments can be set freely, and callback_args is passed.
    callback_args :  None, list, tuple or dict, default None
        Arguments passed to your callback function.
    extract_body : bool, default True
        Whether to extract the message body.
    visibility_timeout : int, default 300
        Message visibility timeout seconds.
    interval_seconds : float, default 1.0
        Message reception interval seconds.
    max_workers : int, default 1
        Max number of concurrent threads or processes.
    process_worker : bool, default False
        If this is True, processes is used instead of threads.
    aws_profile_dict : None or dict, default None
        Additional AWS profile. (credentials, region, etc)
    """
    with ProcessPoolExecutor(max_workers=max_workers) if process_worker \
            else ThreadPoolExecutor(max_workers=max_workers) as executor:
        loop = asyncio.get_event_loop()
        loop.call_soon(_poll, loop, executor, callback, callback_args, aws_profile_dict, queue_url,
                       extract_body, visibility_timeout, interval_seconds)
        loop.run_forever()
        loop.close()


_session = None


def _get_session(aws_profile_dict):
    global _session

    if _session is None:
        if aws_profile_dict is not None:
            aws_profile_dict["service_name"] = "sqs"
        else:
            aws_profile_dict = {"service_name": "sqs"}

        _session = boto3.client(**aws_profile_dict)

    return _session


def _poll(loop, executor, callback, callback_args, aws_profile_dict, queue_url,
          extract_body, visibility_timeout, interval_seconds):
    sqs = _get_session(aws_profile_dict)

    messages = _receive(sqs, queue_url, visibility_timeout)

    if len(messages) > 0:
        executor.submit(_execute, aws_profile_dict, queue_url, callback,
                        callback_args, messages, extract_body)

    loop.call_later(interval_seconds, _poll, loop, executor, callback, callback_args, aws_profile_dict,
                    queue_url, extract_body, visibility_timeout, interval_seconds)


def _receive(sqs, queue_url, visibility_timeout, max_number_of_messages=1):
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=max_number_of_messages,
        VisibilityTimeout=visibility_timeout,
    )

    if "Messages" in response:
        messages = [m for m in response["Messages"]]
    else:
        messages = []

    return messages


def _execute(aws_profile_dict, queue_url, callback, callback_args, messages, extract_body):
    for message in messages:
        body = message["Body"] if extract_body else message

        if isinstance(callback_args, dict):
            deletable = callback(body, **callback_args)
        elif isinstance(callback_args, tuple) or isinstance(callback_args, list):
            deletable = callback(body, *callback_args)
        else:
            deletable = callback(body)

        if not isinstance(deletable, bool):
            raise TypeError("`callback` function must return bool. (whether its message can be deleted)")

        if deletable:
            sqs = _get_session(aws_profile_dict)
            sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=message["ReceiptHandle"])
