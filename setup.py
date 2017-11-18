from setuptools import setup, find_packages

setup(
    name='greek-wines',
    version='1.0',
    packages=['houseofwine_gr', ],
    url='https://tselai.com/greek-wines-data-analysis',
    license='The MIT License (MIT) Copyright © 2017 Florents Tselai.',
    description='Wine Market Data',
    long_description=open('README.md', 'r').read(),
    author='Florents Tselai',
    author_email='florents.tselai@gmail.com',
    install_requires=open('requirements.txt').read().splitlines(),
)
