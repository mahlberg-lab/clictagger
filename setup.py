from setuptools import setup, find_packages

requires = [
    'pybtex',
    'pyicu',
    'unidecode',
]

tests_require = [
    'pytest',
    'pytest-cov',
]

setup(
    name="clic",
    description='CLiC web API',
    author='Jamie Lentin',
    author_email='jamie.lentin@shuttlethread.com',
    url='https://github.com/birmingham-ccr/clic',
    packages=find_packages(),
    install_requires=requires,
    extras_require=dict(
       testing=tests_require,
    ),
    entry_points={
        'console_scripts': [
            'region_preview=clic.migrate.region_preview:script_region_preview',
        ],
    },
)
