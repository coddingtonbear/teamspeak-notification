from setuptools import setup

from teamspeaknotifier import get_version

setup(
    name='teamspeaknotifier',
    version=get_version(),
    url='https://bitbucket.org/latestrevision/teamspeak-notification/',
    description='Show unobtrusive notifications when certain things happen in teamspeak.',
    author='Adam Coddington',
    author_email='me@adamcoddington.net',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Linux',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    packages=['teamspeaknotifier',],
    entry_points={'console_scripts': [
        'teamspeak-notifier = teamspeaknotifier:run_from_cmdline']},
    install_requires = [
            'teamspeak3>=1.3',
        ]
)
