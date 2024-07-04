from setuptools import setup, find_packages

setup(
    name='crypto_arbitrage_bot',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'binance',
        'bybit',
        'requests',
        'schedule',
        'tabulate',
    ],
    entry_points={
        'console_scripts': [
            'crypto_arbitrage_bot=bot:main',
        ],
    },
    license='MIT',
    author='Your Name',
    author_email='your.email@example.com',
    description='A crypto arbitrage bot for Binance and Bybit.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/crypto_arbitrage_bot',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
