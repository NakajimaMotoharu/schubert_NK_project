"""Only current758 eightactual streams plus frozen748 same-source3513host."""
from pathlib import Path
from pg730_native_counter import source as previous
from pg761_current_binding import bind
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():return replace(bind(previous()),(
    ('pg713-expiry-six-host-v1','pg748-closing-six-host-v1'),
    ('5f6a57015fb30d8f2097e594370d558ac6202a9d5d2ed98ce0108494cc7f524a','d4d3ba09651c75d15334e2775fa9a1ae8f8362e2fa92d9e8ebb57c1d8667d96e'),
    ("tests']==3502","tests']==3513")))


def namespace():
    env={'__file__':str(R/'pg766_native_counter.py'),'__name__':'current750_native'}
    exec(compile(source(),'<current750 exacteight>','exec'),env);return env


def strict(proof):
    assert type(proof)is dict and type(proof.get('actualExit'))is int and proof['actualExit']==0
    assert proof['genuineCompletion']['genuineRootDone']is True and proof['genuineCompletion']['genuinePid1StartDone']is True


def code(hashes,proof,seals):strict(proof);return namespace()['code'](hashes,proof,seals)
def catalog(before_sha):return namespace()['catalog'](before_sha)


if __name__=='__main__':
    env=namespace();previous_code=env['code']
    def strict_code(hashes,proof,seals):strict(proof);return previous_code(hashes,proof,seals)
    env['code']=strict_code;env['main']()
