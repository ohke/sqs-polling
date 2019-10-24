# sqs-polling
`sqs-polling` is simple AWS SQS daemon. The following is all.
- Polls SQS at regular intervals.
- Receives messages and executes your callback.
- If your callback function returns True, deletes the message.

## Installation
```
$ pip install sqs-polling
```

## Usage
The key function is `sqs_polling`, please check its interface.

The simplest usage is below.
```python
from sqs_polling import sqs_polling


def your_callback(message, greeting):
    print(greeting + message["name"])
    return True


your_queue_url="https://sqs.your-region.amazonaws.com/XXXXXXXXXXXX/your-sqs",
sqs_polling(queue_url=your_queue_url, callback=your_callback, callback_args={"greeting": "Hello, "})
```

### Callback
Your callback function must return 1 bool value.
If True, deletes the processed message.
If False, the message is remaining in your SQS and reprocessed after `visibility_timeout` seconds. It is recommended to return False if message processing fails.

## Configuration

### AWS account profile
In the example above, explicit AWS account profiles is omitted.

If explicit authentication is required, you can access SQS by setting additional profiles in `aws_profile_dict` argument.

```python
your_aws_profile = {
    "region_name": "your-region",
    "aws_access_key_id": "XXXXXXXXXXXXXXXXXXXX",
    "aws_secret_access_key": "YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY",
}

sqs_polling(queue_url=your_queue_url, callback=your_callback, aws_profile_dict=your_aws_profile)
```

### Polling
The arguments related to polling settings are as follows.

- `extract_body`: Whether to extract the message body. (default: True)
  - The `body` here refers to `$.Messages.Body` JSON element of SQS messages.
- `interval_seconds`: Message reception interval seconds. (default: 1.0)
- `visibility_timeout`: Message visibility timeout seconds. (default: 300)

### Concurrency
`sqs-polling` can process messages in parallel using threads or processes. It can be controlled by the following arguments.

- `max_workers`: Max number of concurrent threads or processes. (default: 1)
- `process_worker`: If this is True, processes is used instead of threads. (default: False) 

```python
# Parallel processing with up to 64 threads.
sqs_polling(queue_url=your_queue_url, callback=your_callback, max_workers=64)

# Parallel processing with up to 4 processes.
sqs_polling(queue_url=your_queue_url, callback=your_callback, process_worker=True, max_workers=4)
```