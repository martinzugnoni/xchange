from setuptools import setup
from setuptools.command.test import test as TestCommand

import xchange


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ["--cov", "xchange", "tests/"]

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import sys, pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='xchange',
    version=xchange.__version__,
    description=("Many cryptocurrency exchange APIs, a single and unified API client"),
    url='https://github.com/martinzugnoni/xchange',
    download_url=(
        "https://github.com/martinzugnoni/xchange/tarball/{version}".format(
            version=xchange.__version__)),
    author='Martin Zugnoni',
    author_email='martin.zugnoni@gmail.com',
    license='MIT',
    packages=['xchange'],
    maintainer='Martin Zugnoni',
    tests_require=[
        'requests==2.18.4',
        'cached-property==1.4.2',
        'pytest==3.5.1',
        'pytest-cov==2.5.1',
        'responses==0.9.0',
    ],
    zip_safe=False,
    cmdclass={'test': PyTest},
)
