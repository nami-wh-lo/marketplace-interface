from setuptools import setup, find_packages

setup(
    name="marketplace_handler",
    version="1.0.0",
    author="your_nickname",
    author_email="dulugov@gmail.com",
    description="Module to interact with marketplaces",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.6.1",
        "requests>=2.31.0",
    ],
)
