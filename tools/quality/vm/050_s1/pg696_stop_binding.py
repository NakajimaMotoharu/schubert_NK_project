"""New actual PG693 proof only, unchanged ordered owned TERM protocol."""
import datetime
from pathlib import Path
import uuid
from pg692_retention_sources import replace

R=Path(__file__).resolve().parent
RUN='8633b77f-77dc-4a78-88b4-41165f159b43'
CUTOFF='2026-10-09T00:43:10.150245Z'
SOURCE='9bd50536f692610036a0ed8b83e0a8b35fe2a66f'


def source(proof):
    assert type(proof)is dict and type(proof.get('actualExit'))is int and proof['actualExit']==0
    assert proof.get('productionSource')==SOURCE and proof.get('batchRun')==RUN and proof.get('cutoff')==CUTOFF
    activation=proof['activation'];u=uuid.UUID(activation)
    assert str(u)==activation and u.version==4 and activation not in ('ad15ac4a-8d8e-4970-bcb3-2e000050ce77','7d381b67-b37b-48c6-99ac-e04a336f887d','970bbce1-6bba-4db0-ace1-680ee7dfde92')
    end=proof['genuineCompletion']['endMonotonicUs'];assert type(end)is int and 119288459330<=end<=121088459330
    assert datetime.datetime.fromisoformat(proof['parentEndedUTC'].replace('Z','+00:00'))>=datetime.datetime.fromisoformat(CUTOFF.replace('Z','+00:00'))
    raw=(R/'pg642_stop_binding.py').read_text()
    return replace(raw,(
        ('Pg642','Pg696'),('pg642','pg696'),('PG642','PG696'),
        ('36fe7a0b938489d61d17d49c1c30a6fbbef699d5',SOURCE),
        ('57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe','076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480'),
        ("'PG600', 'PG631'", "'PG600', 'PG682'"),
        ('e49243d5-de84-4714-8612-6912ddc17e9e',RUN),
        ('2026-10-08T18:32:42.140966Z',CUTOFF),
        ('2026-10-08T18:32:42.140966+00:00','2026-10-09T00:43:10.150245+00:00'),
        ('7d381b67-b37b-48c6-99ac-e04a336f887d',activation),
        ('293d218b06454bd1a8ff350bb93de2d5','6b3dd954959c43c1bbac2164ec9d0c6b'),
        ('103062293730','119288459330'),('104862293730','121088459330'),
        ('104329','122726'),('1522744','2146618'),
        ('pg640-completed-readonly-v1','pg693-completed-readonly-v1'),
        ('pg635-resume-preparation-v1','pg685-completed-activate-v1'),
        ("r'2026-10-08T[0-9:]{8}","r'2026-10-09T[0-9:]{8}"),
    ))


def generate(proof):
    env={'__file__':str(R/'pg696_stop_binding.py'),'__name__':'new_current_owned_stop'}
    exec(compile(source(proof),'<new actual current stop proof>','exec'),env)
    return env['generate'](proof)


def bindings(proof):
    env={'__file__':str(R/'pg696_stop_binding.py'),'__name__':'new_current_owned_stop'}
    exec(compile(source(proof),'<new actual current stop proof>','exec'),env)
    return env['bindings'](proof)
