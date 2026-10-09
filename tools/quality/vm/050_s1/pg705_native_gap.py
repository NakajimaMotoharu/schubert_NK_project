"""Offline current nine/host6 exact XML, original manifests stay unchanged."""
from pathlib import Path
from pg700_native_gap import source as previous
from pg662_sources import replace

R = Path(__file__).resolve().parent


def source():
    raw = replace(previous(), (
        ('pg700-current-native-gap-v1', 'pg705-current-native-gap-v1'),
        ('assert len(data) == 14', "addition=W/'pg704-current-nine-native-v1';assert sha(addition/'manifest.safe.json')=='f5c612e6a3445c4ead6c103da1a8d77e4d323aca9ad02a525c1f426c6da9ae11'\n    extra=json.loads((addition/'manifest.safe.json').read_bytes());assert extra['actualExit']==0 and extra['source']==record['productionSource']and extra['qualifiedSingleSessions']==9 and extra['previousUnionSha256']==sha(cohort/'manifest.safe.json')and not extra['otherSourceStreamsImported']\n    stream=addition/'bootstrap.exec';assert sha(stream)==extra['bootstrap']['sha256'];data.append(stream)\n    record={**record,'moduleCounters':extra['moduleCounters']}\n    assert len(data)==15"),
        ("'parentManifestSha256':sha(cohort/'manifest.safe.json')", "'parentManifestSha256':sha(addition/'manifest.safe.json')"),
    ))
    return raw


if __name__ == '__main__':
    exec(compile(source(), '<same source nine qualified gap>', 'exec'),
         {'__file__': str(R / 'pg705_native_gap.py'), '__name__': '__main__'})
