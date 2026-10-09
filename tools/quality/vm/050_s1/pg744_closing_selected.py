"""BUG925: explicit four leaf reactor; old PG743 failure retained, no root -am prefix lookup."""
from pathlib import Path
from pg662_sources import replace

R = Path(__file__).resolve().parent


def source():
    return replace((R / 'pg743_closing_selected.py').read_text(), (
        ('pg743-closing-selected-v1', 'pg744-closing-selected-v1'),
        ("'src/schubert-nk-bootstrap,src/schubert-nk-api', '-am',", "'src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api',"),
    ))


if __name__ == '__main__':
    env = {'__file__':str(R / 'pg744_closing_selected.py'), '__name__':'closing_four_leaves'}
    exec(compile(source(), '<four explicit leaf selected>', 'exec'), env)
    env['main']()
