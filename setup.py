from setuptools import setup, find_packages

setup(
    name='jmbo-competition',
    version='0.0.4',
    description='Jmbo competition app.',
    long_description = open('README.rst', 'r').read(),
    author='Praekelt International',
    author_email='dev@praekelt.com',
    license='BSD',
    url='http://github.com/praekelt/jmbo-competition',
    packages = find_packages(),
    install_requires = [
        'jmbo',
        'django-ckeditor',
        'django-preferences',
    ],
    tests_require=[
        'django-setuptest',
    ],
    test_suite="setuptest.SetupTestSuite",
    include_package_data=True,
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    zip_safe=False,
)

