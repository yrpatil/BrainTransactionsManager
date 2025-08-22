#!/usr/bin/env python3
"""
Setup script for BrainTransactionsManager
Blessed by Goddess Laxmi for Infinite Abundance 🙏
"""

from setuptools import setup, find_packages

setup(
    name="braintransactions",
    version="1.1.0",
    description="Modular transactional system for financial operations - Blessed by Goddess Laxmi",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="AlgoChemist Team",
    author_email="team@algochemist.ai",
    url="https://github.com/algochemist/BrainTransactionsManager",
    
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "python-dotenv>=0.19.0",
        "pydantic>=1.10.0",
        
        # Database
        "psycopg2-binary>=2.9.0",
        "sqlalchemy>=1.4.0",
        
        # Trading APIs
        "alpaca-trade-api>=3.0.0",
        
        # Utilities
        "python-dateutil>=2.8.0",
        "pytz>=2022.1",
        "requests>=2.28.0",
        
        # Testing (dev)
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.0.0",
    ],
    
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0", 
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ],
        "telegram": [
            "python-telegram-bot>=20.0",
        ],
    },
    
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    
    keywords="trading, transactions, financial, alpaca, portfolio, risk-management",
    
    entry_points={
        "console_scripts": [
            "laxmi-yantra=braintransactions.modules.laxmi_yantra.cli:main",
            "brain-transactions=braintransactions.core.cli:main",
        ],
    },
    
    include_package_data=True,
    zip_safe=False,
)
