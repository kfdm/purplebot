from fabric.api import local
import os


def clean():
    'Remove temporary files'
    _clean_me = []
    for root, dirs, files in os.walk('.'):
        for f in files:
            if f.endswith('.pyc'):
                _clean_me.append(os.path.join(root, f))
    for clean_me in _clean_me:
        try:
            print 'Removing:', clean_me
            os.unlink(clean_me)
        except:
            pass


def test():
    'Run tests'
    local('nosetests --with-coverage --cover-html --cover-package=purplebot')
