from os.path import expanduser
from setuptools import setup, find_packages 


setup(
    name='ack',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'newspaper',
        'beautifulsoup4',
        'delorean',
        'numpy'
    ],
    dependency_links = [
    ],
    data_files=[('config', ['ack.cfg'])],
    entry_points="""
        [console_scripts]
        ack=ack.cli:cli
    """,
    test_suite='tests',
)
