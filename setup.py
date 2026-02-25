from setuptools import setup, find_packages

setup(
    name="espx",
    version="0.1.0",
    description="ESPx secure API key management vault",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "cryptography>=41.0.0",
        "pyotp>=2.9.0",
        "qrcode>=7.4.2",
        "click>=8.1.0",
    ],
    entry_points={
        "console_scripts": [
            "espx=espx.cli:cli",
        ],
    },
)
