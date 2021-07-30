from setuptools import setup, find_packages

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
)
