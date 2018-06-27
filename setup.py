from setuptools import setup

setup(
    name='couchreq',
    version='1.0.0a1',
    description='Python module for some basic level CouchDB interactions.',
    author='Sami Ikonen',
    author_email='sami.ikonen@live.fi',
    url='https://github.com/Samiikon/couchreq',
    license='MIT',
    packages=['couchreq'],
    include_package_data=True,
    install_requires=[
        'requests',
    ]
)
