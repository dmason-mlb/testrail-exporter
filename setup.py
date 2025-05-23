from setuptools import setup, find_packages

setup(
    name="testrail-exporter",
    version="1.0.6",
    packages=find_packages(),
    package_data={
        "": ["*.png", "*.ico", "*.icns"],
    },
    include_package_data=True,
    install_requires=[
        "requests>=2.28.0",
        "Pillow>=9.2.0",
        "pandas>=1.3.0",
    ],
    entry_points={
        "console_scripts": [
            "testrail-exporter=testrail_exporter.main:main",
        ],
    },
    author="Doug Mason",
    author_email="douglas.mason@mlb.com",
    description="Export test cases from TestRail for importing into X-ray",
    keywords="testrail, export, xray, testing",
    python_requires=">=3.6",
)