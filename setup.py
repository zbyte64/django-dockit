#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

VERSION = '0.0.12'
LONG_DESC = """\
"""

setup(name='django-dockit',
      version=VERSION,
      description="",
      long_description=LONG_DESC,
      classifiers=[
          'Programming Language :: Python',
          'Operating System :: OS Independent',
          'Natural Language :: English',
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
      keywords='django',
      maintainer = 'Jason Kraus',
      maintainer_email = 'zbyte64@gmail.com',
      url='http://github.com/webcube/django-dockit',
      license='New BSD License',
      packages=find_packages(exclude=['test_environment', 'tests']),
      test_suite='tests.setuptest.runtests',
      tests_require=(
        'pep8==1.3.1',
        'coverage',
        'django',
        'Mock',
        'nose',
        'django-nose',
      ),
      include_package_data = True,
  )
