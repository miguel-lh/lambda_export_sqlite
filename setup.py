"""
Setup script para el proyecto Lambda Export SQLite.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lambda-export-sqlite",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Lambda para exportar datos de PostgreSQL a SQLite",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/lambda-export-sqlite",
    packages=find_packages(exclude=["tests", "tests.*", "events"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.11",
    install_requires=[
        "psycopg2-binary>=2.9.9",
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.3",
        "pydantic-settings>=2.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "moto>=4.2.10",
            "black>=23.12.1",
            "flake8>=7.0.0",
            "mypy>=1.7.1",
            "pylint>=3.0.3",
            "isort>=5.13.2",
            "ipython>=8.18.1",
        ],
    },
)
