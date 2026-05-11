from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="ai-travel-agent",
    version="0.1",
    author="Eduardo dos Santos Sousa",
    packages=find_packages(),
    install_requires=requirements,
)
