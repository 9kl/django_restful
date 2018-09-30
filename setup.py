from setuptools import setup, find_packages

setup(
    name='django-restful',
    version='0.0.6',
    author='bigtiger',
    author_email='chinafengheping@gmail.com',
    url='http://www.hshl.ltd',
    description=u'django_restful',
    packages=find_packages(),  # include all packages under src
    include_package_data=True,    # include everything in source control
    install_requires=[
        'djangorestframework>=3.3.1',
        'six'
    ]
)
