"""BUG1049 corrected cold guard; new-only A01 slots, old waiting run retained."""
import ast
from pg1189_current_resume_a01 import code as previous


def code():
    s = previous().replace('pg1189', 'pg1190').replace('PG1189', 'PG1190')
    ast.parse(s);return s


if __name__ == '__main__':
    env = {'__file__': __file__, '__name__': 'current_resume_A01_v2'}
    exec(compile(code(), '<corrected cold actual A01>', 'exec'), env);env['main']()
