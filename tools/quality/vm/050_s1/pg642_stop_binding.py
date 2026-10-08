"""Fixed new completed cohort for unchanged SSC190/191 ordered owned TERM protocol.

Input is the genuine PG640 readonly receipt, not live process guesses or old evidence.
Generation only; never starts/stops/deploys. Generated files are new private artifacts.
"""
import re
from pathlib import Path

R = Path(__file__).resolve().parent
SOURCE = '36fe7a0b938489d61d17d49c1c30a6fbbef699d5'
MANIFEST = '57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe'


def require(value):
    if not value:
        raise ValueError('fixed genuine current stop binding refused')


def bindings(proof):
    require(type(proof) is dict and proof.get('actualExit') == 0
            and proof.get('productionSource') == SOURCE
            and proof.get('batchRun') == 'e49243d5-de84-4714-8612-6912ddc17e9e'
            and proof.get('cutoff') == '2026-10-08T18:32:42.140966Z'
            and proof.get('activation') == '7d381b67-b37b-48c6-99ac-e04a336f887d'
            and proof['genuineCompletion']['genuinePid1StartDone'] is True
            and proof['genuineCompletion']['genuineRootDone'] is True)
    require(type(proof['beforeSha256']) is str and re.fullmatch('[0-9a-f]{64}', proof['beforeSha256']) is not None)
    end = proof['genuineCompletion']['endMonotonicUs']
    require(type(end) is int and 103062293730 <= end <= 104862293730)
    require(type(proof['parentEndedUTC']) is str and re.fullmatch(r'2026-10-08T[0-9:]{8}\.[0-9]{6}Z', proof['parentEndedUTC']) is not None)
    result = [
        ('Pg611NativeStop', 'Pg642NativeStop'), ('Pg611NativeArgumentTest', 'Pg642NativeArgumentTest'),
        ('pg611', 'pg642'), ('PG611', 'PG642'),
        ('23b14a44b10504172e030bbd6625926bf049fb5c', SOURCE),
        ('a6342b8a764565cdfea256a781029d419888c7b58c0c3f9b00685e30feaa786f', MANIFEST),
        ('PG600', 'PG631'),
        ('3a53b979-fa01-47dd-92a6-7b26affcfb5c', 'e49243d5-de84-4714-8612-6912ddc17e9e'),
        ('2026-10-08T15:32:46.368375Z', '2026-10-08T18:32:42.140966Z'),
        ('970bbce1-6bba-4db0-ace1-680ee7dfde92', '7d381b67-b37b-48c6-99ac-e04a336f887d'),
        ('5a1acaa0c35e484c979401e3b6dfb36a', '293d218b06454bd1a8ff350bb93de2d5'),
        ('86264628081', '103062293730'), ('88064628081', '104862293730'),
        ('87761979588', str(end)), ('87863', '104329'), ('1207482', '1522744'),
        ('8d9888702641b29b9feff811cebc94f86d97de96330a43fb0c29c6959f98bf47', proof['beforeSha256']),
        ('pg609-completed-readonly-v1', 'pg640-completed-readonly-v1'),
        ('pg604-completed-activate-v1', 'pg635-resume-preparation-v1'),
    ]
    units = proof['ownedUnits']
    old = {
        'caddy.service': ('1460173', 'fd0cd00933ce43b88634c43faef7a0ef'),
        'schubert-nk-web.service': ('1454010', '866af4c303904f1e998a5a50f6ccc716'),
        'schubert-nk-api.service': ('1451527', '4db7f8a4637a4b9f909de4d319677179'),
        'artemis.service': ('1304653', '1a7bc5e9a7734bbb9a657bf11fac7dbe')}
    for unit, (pid, invocation) in old.items():
        v = units[unit]
        require(v['ActiveState'] == 'active' and v['SubState'] == 'running'
                and type(v['MainPID']) is str and re.fullmatch('[1-9][0-9]{0,8}', v['MainPID']) is not None
                and type(v['InvocationID']) is str and re.fullmatch('[0-9a-f]{32}', v['InvocationID']) is not None)
        result.extend(((pid, v['MainPID']), (invocation, v['InvocationID'])))
    return result


def generate(proof):
    mapping = bindings(proof)
    names = ('Pg611NativeStop.java', 'Pg611NativeArgumentTest.java', 'pg611_native_refs.py',
             'pg611_native_owned_stop.py', 'pg611_parent_receipt.py', 'pg611_durable.py')
    result = {}
    for name in names:
        raw = (R/name).read_text()
        if name == 'Pg611NativeStop.java':
            old = '!done.endedAt().isAfter(epoch.activation().run().cutoff().plusSeconds(1800))'
            require(raw.count(old) == 1)
            raw = raw.replace(old, 'done.endedAt().equals(java.time.Instant.parse("'+proof['parentEndedUTC']+'"))')
        for old, new in mapping:
            raw = raw.replace(old, new)
        new_name = name.replace('Pg611', 'Pg642').replace('pg611', 'pg642')
        result[new_name] = raw
    for name in ('pg526_term_witness.py', 'pg526_native_term_witness.py'):
        result[name] = (R/name).read_text()
    return result
