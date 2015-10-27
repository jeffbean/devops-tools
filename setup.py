# coding=utf-8
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name='desktop-tools',
    version='1.0',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    url='',
    license='',
    author='Jeff Bean ',
    author_email='jeff.bean@hds.com',
    description='Tools package to make things a bit easier.',
    entry_points={
        'console_scripts': [
            'buildpak = bin.build_tools:main',
        ],
    },
    exclude_package_data={'': ['.gitignore']},
    install_requires=open('requirements.txt').read(),
    setup_requires=open('setup_requirements.txt').read(),
)
