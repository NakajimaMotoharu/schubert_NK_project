"""Offline qualified current17+host6 coordinates; no actual VM operation."""
import hashlib
import json
from pathlib import Path
from pg660_native_gap import code as previous

R=Path(__file__).resolve().parent;W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def code(digest):
    raw=previous(digest)
    for a,b in (('pg658-same-source-sixteen-native-v1','pg666-current-seventeen-native-v1'),('pg660-current-native-gap-v1','pg668-current-native-gap-v1'),
                ('assert len(data)==22',"p=cohort/'bootstrap.exec';assert sha(p)==record['bootstrap']['sha256'];data.append(p)\n    assert len(data)==23")):
        assert a in raw;raw=raw.replace(a,b)
    return raw


def main():
    p=W/'pg666-current-seventeen-native-v1/manifest.safe.json';v=json.loads(p.read_bytes())
    assert v['actualExit']==0 and v['qualifiedSingleSessions']==17 and v['source']=='36fe7a0b938489d61d17d49c1c30a6fbbef699d5'and not v['otherSourceStreamsImported']
    env={'__file__':str(R/'pg668_gap.py'),'__name__':'current_gap'};exec(compile(code(hashlib.sha256(p.read_bytes()).hexdigest()),'<qualified current17 XML>','exec'),env);env['main']()


if __name__=='__main__':main()
