from setuptools import setup, find_packages

setup(
    name="insighta-cli",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "typer",
        "rich",
        "httpx",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "insighta=insighta.main:app",
            # 'insighta' command → runs app() in insighta/main.py
        ],
    },
)