import setuptools
import xchange


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name='xchange',
    version=xchange.__version__,
    description=("Many cryptocurrency exchange APIs, a single and unified API client"),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/martinzugnoni/xchange',
    download_url=(
        "https://github.com/martinzugnoni/xchange/tarball/{version}".format(
            version=xchange.__version__)),
    author='Martin Zugnoni',
    author_email='martin.zugnoni@gmail.com',
    license='MIT',
    packages=setuptools.find_packages(),
    maintainer='Martin Zugnoni',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
