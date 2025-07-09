from setuptools import setup, find_packages

# Read requirements.txt
with open('requirements.txt') as f:
    required = f.read().splitlines()

# Read README.md
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='crypto_arbitrage',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},  # Tell setuptools packages are under src
    install_requires=required,  # Use requirements from requirements.txt
    entry_points={
        'console_scripts': [
            'crypto-arbitrage=main:main',  # Updated entry point
        ],
    },
    # Metadata
    author='Your Name',
    author_email='your.email@example.com',
    description='A crypto arbitrage bot for Binance and KuCoin exchanges',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/crypto_arbitrage',
    license='MIT',
    # Project classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Office/Business :: Financial :: Investment',
    ],
    # Project requirements
    python_requires='>=3.8',
    # Include additional files
    package_data={
        '': ['README.md', 'LICENSE'],
    },
)