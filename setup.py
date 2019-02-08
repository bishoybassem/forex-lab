from setuptools import setup

setup(
    name='forex-lab',
    version='0.1.0',
    packages=['forex'],
    install_requires=['requests>=2'],
    python_requires='>=3',
    test_suite="test"
)
