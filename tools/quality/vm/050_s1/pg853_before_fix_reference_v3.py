"""New-only BUG970 callback result correction; v1/v2 preserved."""
from pathlib import Path
R = Path(__file__).resolve().parent
def source():
    namespace = {'__file__': str(R/'pg853_before_fix_reference_v2.py'), '__name__': 'pg853_definition'}
    exec(compile((R/'pg853_before_fix_reference_v2.py').read_text(), '<853v2 definition>', 'exec'), namespace)
    raw = namespace['source']()
    assert raw.count('return null;') == 1
    return raw.replace('pg853-beforefix-reference-v2', 'pg853-beforefix-reference-v3').replace('return null;', 'return run;')
if __name__ == '__main__':
    exec(compile(source(), '<853v3 frozen-source reproduction>', 'exec'), {'__file__': str(R/'pg853_before_fix_reference_v3.py'), '__name__': '__main__'})
