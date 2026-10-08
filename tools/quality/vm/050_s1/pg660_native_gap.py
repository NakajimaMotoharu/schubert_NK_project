"""Offline same-source sixteen qualified stream XML coordinates, no VM operation."""
from pathlib import Path
import hashlib
import json

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def code(union_sha):
    assert type(union_sha)is str and len(union_sha)==64
    raw=(R/'pg615_current_native_gap.py').read_text()
    for old,new in (
        ('pg614-current-eight-native-v1','pg658-same-source-sixteen-native-v1'),
        ('4c178d8e6d2f76f097a315226586bb934041ce1805a5cd79811e2034b3b442c1',union_sha),
        ('23b14a44b10504172e030bbd6625926bf049fb5c','36fe7a0b938489d61d17d49c1c30a6fbbef699d5'),
        ("record['productionSource']", "record['source']"),
        ('pg615-current-native-gap-v1','pg660-current-native-gap-v1'),
        ('pg599-candidate-bootstrap-six-host-v1','pg630-retention-factory-six-host-v1'),
        ("assert sha(host/'manifest.safe.json')==record['frozenHostManifestSha256']", "assert sha(host/'manifest.safe.json')=='067b8a155fe5a137aebb9c732bf800122752cb173ca8a09f3c41087d9efc178b'"),
        ("assert all(sha(p) == record['hostExecHashes'][m] for m, p in zip(modules, data))", "assert all(sha(p)==host_record['moduleResults'][m]['execSha256']for m,p in zip(modules,data))"),
        ("for i, expected in enumerate(record['selected']):\n        p = cohort / (str(i) + '.exec');assert sha(p) == expected['sha256'];data.append(p)\n    assert len(data) == 14",
         "for name in ('pg644-current-eight-native-v1','pg657-normal-eight-native-v1'):\n        qualified=W/name;assert sha(qualified/'manifest.safe.json')==record['qualificationManifests'][name]\n        q=json.loads((qualified/'manifest.safe.json').read_bytes());assert q['actualExit']==0 and q['productionSource']==record['source']\n        for i,expected in enumerate(q['selected']):\n            p=qualified/(str(i)+'.exec');assert sha(p)==expected['sha256'];data.append(p)\n    assert len(data)==22"),
    ):
        assert old in raw,old;raw=raw.replace(old,new)
    return raw


def main():
    p=W/'pg658-same-source-sixteen-native-v1/manifest.safe.json';v=json.loads(p.read_bytes())
    assert v['actualExit']==0 and v['qualifiedCohorts']==2 and v['qualifiedSingleSessions']==16 and not v['otherSourceStreamsImported']
    env={'__file__':str(R/'pg660_native_gap.py'),'__name__':'same_source_gap'}
    exec(compile(code(hashlib.sha256(p.read_bytes()).hexdigest()),'<same qualified16 XML coordinates>','exec'),env);env['main']()


if __name__=='__main__':main()
