"""Strict current ADMIN four-receipt whitelist; no raw secret/session/DB export."""
from pathlib import Path
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():
    return replace((R/'pg706_admin_public.py').read_text(), (
        ('PG702','PG737'),('pg702','pg737'),('pg703-bootstrap-final-v4','pg738-bootstrap-final-v1'),
        ('pg704','pg739'),('gainVsPG698','gainVsPG730'),
        ("['568', '569', '570']","['584', '585', '586']"),
        ("['BOOT702001..002', 'BOOT703001..002', 'BOOT704001..002']","['BOOT737001..003', 'BOOT738001', 'NAT739001']"),
        ("'bugs': ['BUG-922'], 'ykt': ['YKT-691']","'bugs': [], 'ykt': []"),
        ("assert value['actualExit'] == 0 and value['qualifiedSingleSessions'] == 9",
         "assert value['actualExit'] == 0 and value['qualifiedSingleSessions'] == 9 and value['source']=='1ec19782a1afe22d1de75b05f4cd12b8a8a8a172' and hashlib.sha256(raw).hexdigest()=='c638c89363f43431993dfc66028da722193adbff56c2cf7291929c94aa1923e1'"),
        ("assert value['actualExit'] == 0", "assert type(value['actualExit'])is int and value['actualExit'] == 0"),
    ))


if __name__=='__main__':
    exec(compile(source(),'<whitelist currentADMIN only>', 'exec'),
         {'__file__':str(R/'pg741_admin_public.py'),'__name__':'__main__'})
