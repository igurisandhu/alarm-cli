from setuptools import find_packages, setup

setup(
    name="alarm-cli",
    version="1.0.0",
    description="Python CLI Alarm Clock — manage and monitor alarms",
    packages=["src"] + [f"src.{p}" for p in find_packages(where="src")],
    package_dir={"src": "src"},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "alarm=src.main:main",
        ],
    },
    python_requires=">=3.10",
)