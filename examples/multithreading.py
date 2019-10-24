import time
import threading
import os
from sqs_polling import sqs_polling


def multi_callback(message):
    print("Message:", message)
    print("Thread ID:", threading.get_ident())
    print("Process ID:", os.getpid())
    time.sleep(10)
    return True


queue_url = "https://sqs.us-west-2.amazonaws.com/XXXXXXXXXXXX/your-sqs"

# If `process_worker` is True, processes is used instead of threads.
sqs_polling(queue_url=queue_url, callback=multi_callback, max_workers=2)
