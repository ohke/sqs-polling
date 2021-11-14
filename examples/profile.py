from sqs_polling import sqs_polling


def simple_callback(message):
    print(message)
    return True


your_aws_profile = {
    "region_name": "your-region",
    "aws_access_key_id": "XXXXXXXXXXXX",
    "aws_secret_access_key": "YYYYYYYYYYYY",
}

queue_url = "https://sqs.us-west-2.amazonaws.com/ZZZZZZZZZZZZ/your-sqs"

sqs_polling(
    queue_url=queue_url, callback=simple_callback, aws_profile_dict=your_aws_profile
)
