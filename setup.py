import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ctsutils", # Replace with your own username
    version="0.0.1",
    author="C.T. Schnur",
    author_email="534ttl3@gmail.com",
    description="Utility functions for python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/534ttl3/csutils/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
