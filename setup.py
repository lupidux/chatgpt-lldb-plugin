from setuptools import find_packages, setup
import re
from os import path
import subprocess

FILE_DIR = path.dirname(path.abspath(path.realpath(__file__)))
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    install_requirements = f.readlines()

with open(path.join(FILE_DIR, 'main', 'version.py')) as f:
    version = re.match(r'^__version__ = "([\w\.]+)"$', f.read().strip())[1]

if __name__ == "__main__":
    from setuptools.command.develop import develop

    class CustomDevelopCommand(develop):
        def run(self):
            develop.run(self)
            subprocess.run(["chatgpt-lldb-plugin"])

setup(
    name="chatgpt-lldb-plugin",
    version=version,
    author="Carlo Capodilupo",
    author_email="capodilupo@proton.me",
    description="ChatGPT LLDB Plugin", 
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lupidux/chatgpt-lldb-plugin",
    packages=find_packages(),
    package_data={
        'main': [
            'api_connection/*',
            'selenium_connection/*',
        ],
    },
    install_requires=install_requirements,
    classifiers=[
        "Enviroment :: Console"
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Education",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9.2",
    entry_points={
    'console_scripts': [
        'chatgpt-lldb-plugin = main:main',
        ],
    },
    cmdclass={'develop': CustomDevelopCommand},
)
