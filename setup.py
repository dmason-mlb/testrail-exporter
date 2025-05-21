from setuptools import setup, find_packages

setup(
    name="testrail-exporter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "Pillow>=9.2.0",
    ],
    entry_points={
        "console_scripts": [
            "testrail-exporter=testrail_exporter.main:main",
        ],
    },
    author="MLB",
    description="Export test cases from TestRail for importing into X-ray",
    keywords="testrail, export, xray, testing",
    python_requires=">=3.6",
)