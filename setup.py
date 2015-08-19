from setuptools import setup

setup(
    name='find-customers',
    version='0.1.0',
    py_modules=['find_customers'],
    install_requires=[
        'Click',
        'simplejson'
    ],
    url='https://github.com/gagoman/find-customers',
    license='MIT',
    author='gagoman',
    author_email='akhomchenko@gmail.com',
    description='Great circle distance',
    long_description=open('README.md').read(),
    entry_points='''
    [console_scripts]
    find-customers=find_customers:cli
    '''
)
