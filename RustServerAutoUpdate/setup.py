import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rustserverautoupdate-Dateranoth",
    version="0.0.1",
    author="Dateranoth",
    author_email="dateranoth@hotmail.com",
    description="A package to update rust when Oxide updates. Optionall send message to Discord or RCON",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dateranoth/rustserverautoupdatepython",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
