from distutils.core import setup

setup(
    name='MyLittleAgenda',
    version='1.0',
    packages=['flaskr'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)
