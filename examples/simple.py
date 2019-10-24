from sqs_polling import sqs_polling


def simple_callback(message, print_count):
    for _ in range(print_count):
        print(message)

    return True


queue_url = "https://sqs.us-west-2.amazonaws.com/XXXXXXXXXXXX/your-sqs"

# If `extract_body` is False, the entire message including Body is passed as dict.
sqs_polling(queue_url=queue_url, callback=simple_callback, callback_args={"print_count": 3})
