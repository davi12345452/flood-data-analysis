"""Executa uma ou mais etapas batch sob o mesmo lock da execução ao vivo."""
import runpy
import sys

from .paths import PROCESSED
from .storage import exclusive


def main():
    commands = ' '.join(sys.argv[1:]).split(',')
    with exclusive(PROCESSED / '.pipeline.lock'):
        for command in commands:
            module, *args = command.split()
            sys.argv = [module, *args]
            runpy.run_module(module, run_name='__main__')


if __name__ == '__main__':
    main()
