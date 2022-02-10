from distutils.core import setup

setup(
    name='ADAPT Transaction GUI',
    version='0.1dev',
    packages=['adapted'],
    package_data={'': ['*.enaml', 'icons/*.png']},
    scripts=['bin/adapt-gui'],
    install_requires=[
        'bigchaindb-driver>=0.6',
        'enaml>=0.13',
        'pyyaml>=5.4',
    ],
)
