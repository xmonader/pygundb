import setuptools

setuptools.setup(
    name="gundb",
    version="0.1.0",
    url="https://github.com/xmonader/gundb",

    author="Ahmed Youssef",
    author_email="xmonader@gmail.com",

    description="gundb server and client implementations.",
    long_description=open('README.md').read(),

    packages=setuptools.find_packages(),

    install_requires=['flask', 'flask_sockets', 'redis'],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
