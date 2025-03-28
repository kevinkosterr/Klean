from setuptools import setup, find_packages

setup(
    name="Klean",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "b2sdk==2.8.0",
        "toml>=0.10.0",
        "click==8.1.8"
    ],
    entry_points={
      "console_scripts": [
          "klean = run:cli"
      ]
    },
    author="Kevin Koster",
    url='https://github.com/kevinkosterr/Klean',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires=">=3.10"
)
