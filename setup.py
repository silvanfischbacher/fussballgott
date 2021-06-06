import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fussballgott",
    version="0.2.1",
    author="Silvan Fischbacher",
    description="A package to simulate football games, leagues and tournaments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/silvanfischbacher/fussballgott",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(include=["fussballgott"]),
    python_requires=">=3.6",
)
