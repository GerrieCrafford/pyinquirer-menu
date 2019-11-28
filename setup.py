from setuptools import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(name='pyinquirer_menu',
      version='0.1',
      author='Gerrie Crafford',
      description='Package that allows easy multi-level menu creation using PyInquirer',
      long_description=long_description,
      long_description_content_type='text/markdown',
      install_requires=[
          'PyInquirer==1.0.3',
      ],
     )
