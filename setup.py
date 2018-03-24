from setuptools import setup

setup(
    name='jirabot',
    version='0.1',
    py_modules=['jirabot'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        jirabot=jirabot:cli
    ''',
     )
