#!/usr/bin/env python
from migrate.versioning.shell import main

if __name__ == '__main__':
    main(url='sqlite:///inkblot.sqlite', debug='False', repository='inkblot_repository')
