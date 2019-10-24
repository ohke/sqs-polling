import os
from setuptools import setup, find_packages

ROOT = os.path.dirname(__file__)

d = {}
with open(os.path.join(ROOT, "sqs_polling", "__version__.py")) as f:
    exec(f.read(), d)

version = d["__version__"]

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="sqs-polling",
    version=version,
    author="Kenta Onishi",
    author_email="ohke.develop@gmail.com",
    description="Polls AWS SQS messages and executes your callback.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ohke/sqs-polling",
    packages=find_packages(exclude=["tests*"]),
    install_requires=["boto3"],
    python_requires="~=3.5",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
