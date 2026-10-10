"""Fresh same-source observer before current canonical same-active resume."""
import ast
from pg1112_fresh_cold_observer import source as previous


def source():
    s = previous().replace('pg1112', 'pg1183').replace('PG1112', 'PG1183')
    old = "pg1106-ordinary-cold-before-v1/manifest.safe.json"
    if s.count(old) != 1:raise ValueError('fixed independent post admission refused')
    s = s.replace(old, 'pg1182-canonical-runtime-post-v1.safe.json')
    ast.parse(s);return s


if __name__ == '__main__':exec(compile(source(), '<fresh canonical resume observer>', 'exec'), {'__file__': __file__, '__name__': '__main__'})
