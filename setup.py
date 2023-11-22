from setuptools import setup, find_packages

setup(
    name='mypackage',
    version='0.1',
    author= 'Daxit Golakiya',
    
    packages=find_packages(),
    install_requires=[ 
        "requests>=2.25.1",
        "pandas>=1.2.0"
        "beautifulsoup4>=4.9.3"
    ],
    python_requires="3.6"
)
