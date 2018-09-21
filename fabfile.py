import nose
import os
import sys

from fabric.api import *

sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))


def test(suite):
    nose.run(argv=['-w', os.path.join('tests', suite), '-vv', '--with-cover', '--cover-package=mysqlkit'])


def build():
    local('python2 setup.py sdist bdist_wheel')
    local('python3 setup.py bdist_wheel')


def release(repo='test'):
    if not os.path.exists(os.path.expanduser('~/.pypirc')):
        if not all(map(lambda e: e in os.environ, ['TWINE_USERNAME', 'TWINE_PASSWORD'])):
            abort('Cannot upload without TWINE_USERNAME and TWINE_PASSWORD env variables')

    REPOSITORIES = {
        'test': 'https://test.pypi.org/legacy/',
        'pypi': 'https://upload.pypi.org/legacy/',
    }
    local('twine upload --repository-url={repo} dist/*'.format(repo=REPOSITORIES[repo]))