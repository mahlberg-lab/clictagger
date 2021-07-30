from setuptools import setup, find_packages
import codecs
import os.path

# https://packaging.python.org/guides/single-sourcing-package-version/
def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

requires = [
    'pyicu>=2.6',
    'unidecode',
]

tests_require = [
    'pytest',
    'pytest-cov',
]

setup(
    name="clictagger",
    version="0.0.1",
    description='CLiC region tagging',
    long_description=read('README.rst'),
    classifiers=[
        # https://pypi.org/classifiers/
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    author='Jamie Lentin',
    author_email='jamie.lentin@shuttlethread.com',
    url='https://github.com/mahlberg-lab/clictagger',
    license="MIT",
    packages=find_packages(),
    install_requires=requires,
    extras_require=dict(
       testing=tests_require,
    ),
    entry_points={
        'console_scripts': [
            'clictagger=clictagger.script:clictagger',
        ],
    },
    python_requires='>=3.6',
)
