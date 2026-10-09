"""Whitelisted current748 fullsix3513 receipt; no native/private/session/log export."""
from pathlib import Path
from pg732_public_full import source as previous
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():return replace(previous(),(
    ('pg713-expiry-six-host-v1','pg748-closing-six-host-v1'),('PG713-full-public-v1','PG748-full-public-v1'),
    ('5f6a57015fb30d8f2097e594370d558ac6202a9d5d2ed98ce0108494cc7f524a','d4d3ba09651c75d15334e2775fa9a1ae8f8362e2fa92d9e8ebb57c1d8667d96e'),
    ('(3502, 517, 1614)','(3513, 519, 1616)'),
    ('574_PG713_Expiry候補全六回帰仕様.md','588_PG746_748_closing資格・全6回帰仕様.md')))


if __name__=='__main__':
    env={'__file__':str(R/'pg763_public_full.py'),'__name__':'safe_current748_full'}
    exec(compile(source(),'<exact748 full-public>','exec'),env);env['main']()
