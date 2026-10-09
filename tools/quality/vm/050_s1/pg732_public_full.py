"""Whitelisted exact-source whole-six receipt; raw sessions/logs excluded."""
from pathlib import Path
from pg683_public_full import source as previous
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():
    return replace(previous(), (
        ('pg680-owner-six-host-v1','pg713-expiry-six-host-v1'),
        ('PG680-full-public-v1','PG713-full-public-v1'),
        ('b710c69b798fcd14b35644541aed835689d81e6f0cbf40c3d67786e014f599e6','5f6a57015fb30d8f2097e594370d558ac6202a9d5d2ed98ce0108494cc7f524a'),
        ('(3489, 516, 1612)','(3502, 517, 1614)'),
        ('552_PG680_681_所有経路全6回帰仕様.md','574_PG713_Expiry候補全六回帰仕様.md'),
    ))


if __name__=='__main__':
    env={'__file__':str(R/'pg732_public_full.py'),'__name__':'whitelist_expiry_full'}
    exec(compile(source(),'<exact six public results>','exec'),env);env['main']()
