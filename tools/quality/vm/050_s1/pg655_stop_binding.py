"""Generate the approved ordered stop against the new genuine normal receipt only."""
import datetime
from pathlib import Path
import uuid

R=Path(__file__).resolve().parent


def source(proof):
    assert type(proof)is dict and proof.get('actualExit')==0
    assert proof.get('productionSource')=='36fe7a0b938489d61d17d49c1c30a6fbbef699d5'
    assert proof.get('batchRun')=='601297d0-a8ba-47da-852b-0ffeae409965'
    assert proof.get('cutoff')=='2026-10-08T21:33:23.332578Z'
    activation=proof['activation'];v=uuid.UUID(activation)
    assert str(v)==activation and v.version==4 and activation not in ('7d381b67-b37b-48c6-99ac-e04a336f887d','970bbce1-6bba-4db0-ace1-680ee7dfde92')
    end=proof['genuineCompletion']['endMonotonicUs']
    assert type(end)is int and 107901545407<=end<=109701545407
    assert type(proof['parentEndedUTC'])is str and datetime.datetime.fromisoformat(proof['parentEndedUTC'].replace('Z','+00:00'))>=datetime.datetime.fromisoformat('2026-10-08T21:33:23.332578+00:00')
    raw=(R/'pg642_stop_binding.py').read_text()
    for old,new in (
        ('Pg642','Pg655'),('pg642','pg655'),('PG642','PG655'),
        ('e49243d5-de84-4714-8612-6912ddc17e9e','601297d0-a8ba-47da-852b-0ffeae409965'),
        ('2026-10-08T18:32:42.140966Z','2026-10-08T21:33:23.332578Z'),
        ('2026-10-08T18:32:42.140966+00:00','2026-10-08T21:33:23.332578+00:00'),
        ('7d381b67-b37b-48c6-99ac-e04a336f887d',activation),
        ('293d218b06454bd1a8ff350bb93de2d5','095f6d1d7f8442b7b2b44ae59a4314f5'),
        ('103062293730','107901545407'),('104862293730','109701545407'),
        ('104329','111752'),('1522744','1826480'),
        ('pg640-completed-readonly-v1','pg653-completed-readonly-v1'),
        ('pg635-resume-preparation-v1','pg647-runtime-retirement-v1'),
    ):
        assert old in raw,old;raw=raw.replace(old,new)
    return raw


def generate(proof):
    env={'__file__':str(R/'pg655_stop_binding.py'),'__name__':'new_normal_stop_binding'}
    exec(compile(source(proof),'<new normal strict genuine owned stop>','exec'),env)
    return env['generate'](proof)


def bindings(proof):
    env={'__file__':str(R/'pg655_stop_binding.py'),'__name__':'new_normal_stop_binding'}
    exec(compile(source(proof),'<new normal strict genuine binding>','exec'),env)
    return env['bindings'](proof)
