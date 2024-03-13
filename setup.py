from setuptools import setup, find_packages


def readme():
    with open("README.md", "r") as f:
        return f.read()


setup(
    name="marketplace_handler",
    version="1.1.1",
    author="derijabyla",
    author_email="dulugov@gmail.com",
    description="Module to interact with marketplaces",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/derijablya/marketplace-interface",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.6.1",
        "requests>=2.31.0",
    ],
)
