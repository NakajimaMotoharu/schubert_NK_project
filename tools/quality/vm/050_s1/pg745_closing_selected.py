"""BUG925 final selected boundary: two changed leaves, unchanged dependency evidence preserved."""
from pathlib import Path
from pg662_sources import replace

R = Path(__file__).resolve().parent


def source():
    return replace((R / 'pg743_closing_selected.py').read_text(), (
        ('pg743-closing-selected-v1', 'pg745-closing-selected-v1'),
        ("'src/schubert-nk-bootstrap,src/schubert-nk-api', '-am',", "'src/schubert-nk-bootstrap,src/schubert-nk-api',"),
        ("    D.mkdir(mode=0o700)", """    assert not subprocess.check_output(['git','diff','--name-only','1ec19782a1afe22d1de75b05f4cd12b8a8a8a172','--','pom.xml','src/schubert-nk-protocol','src/schubert-nk-storage'],cwd=T)
    D.mkdir(mode=0o700)"""),
    ))


if __name__ == '__main__':
    env = {'__file__':str(R / 'pg745_closing_selected.py'), '__name__':'closing_two_leaves'}
    exec(compile(source(), '<two changed leaves; unchanged qualified dependencies>', 'exec'), env)
    env['main']()
