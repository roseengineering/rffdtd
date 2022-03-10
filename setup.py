from distutils.core import setup

exec(open('src/rffdtd/version.py').read())

setup(
    name='rffdtd',
    version=__version__,
    packages=['rffdtd'],
    package_dir={'rffdtd': 'src/rffdtd'},
    install_requires=[
        'torch>=1.10',
        'numpy>=1.18',
    ],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),
    entry_points={
        'console_scripts': [
            'rffdtd = rffdtd.main:main',
        ]
    },
)

