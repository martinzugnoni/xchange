import setuptools
import xchange


with open('README.md', 'r') as fh:
    long_description = fh.read()


def read_requirements(file_name):
    with open(file_name, 'r') as fp:
        return [l.strip() for l in fp if l.strip() and not l.startswith('-r')]


setuptools.setup(
    name='xchange',
    version=xchange.__version__,
    description=('Many cryptocurrency exchange APIs, a single and unified API client'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/martinzugnoni/xchange',
    download_url=(
        'https://github.com/martinzugnoni/xchange/tarball/{version}'.format(
            version=xchange.__version__)),
    author='Martin Zugnoni',
    author_email='martin.zugnoni@gmail.com',
    license='MIT',
    packages=setuptools.find_packages(),
    maintainer='Martin Zugnoni',
    install_requires=read_requirements('requirements/base.txt'),
    tests_require=read_requirements('requirements/dev.txt'),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
