from setuptools import setup, find_packages

setup(
    name="freezing-shared",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'freezing-model>=0.7.0',
        'stravalib>=1.0.0',
    ],
)
