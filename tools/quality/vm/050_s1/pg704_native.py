"""Only current9bd PG698 eight plus actual PG702 ADMIN; old17 never imported."""
from pathlib import Path
from pg662_sources import replace

R = Path(__file__).resolve().parent


def source():
    raw = (R / 'pg666_native.py').read_text()
    raw = replace(raw, (
        ('pg666', 'pg704'), ('PG666', 'PG704'), ('pg664', 'pg702'), ('pg665', 'pg703'),
        ('36fe7a0b938489d61d17d49c1c30a6fbbef699d5', '9bd50536f692610036a0ed8b83e0a8b35fe2a66f'),
        ('65bfe1da3b9e454997f1d899fea9510e', 'd420de6553ef48038a40332c37a8b12e'),
        ('067b8a155fe5a137aebb9c732bf800122752cb173ca8a09f3c41087d9efc178b', 'b710c69b798fcd14b35644541aed835689d81e6f0cbf40c3d67786e014f599e6'),
        ('fa1cd96cc5110f8bb582d7befecb9fd13f66cea63f707b1a03db9e3d5287ef98', 'dc4d6a6d35ff09ee28e39068ac95887c879d0babe362929873047464e7f0f562'),
        ('8767e53ccfc2ea3f434689674dad7395feaef31cec48d53a92bc6fd7eed81c08', '1d70b8f79fb1aa6c1da796b181948334e2a4a7ae962a0365fb5b0c6750c4fb53'),
        ('111645058422', '122580694582'), ('111646651773', '122582163571'),
        ('2142585', '2464638'), ('11164505', '12258069'), ('119175', '128965'),
        ('==514', '==524'), ('pg703-bootstrap-final-v3', 'pg703-bootstrap-final-v4'),
        ("final['full20Fields']", "final['full21Fields']"),
        ('pg630-retention-factory-six-host-v1', 'pg680-owner-six-host-v1'),
        ('pg704-current-seventeen-native-v1', 'pg704-current-nine-native-v1'),
        ('PG704-current-seventeen-native-v1', 'PG704-current-nine-native-v1'),
        ('gainVsPG658', 'gainVsPG698'),
        ("'native17':True", "'native9':True"),
        ('streams.append(stream);assert len(streams)==17', 'streams.append(stream);assert len(streams)==9'),
        ("'qualifiedSingleSessions':17", "'qualifiedSingleSessions':9"),
    ))
    start = raw.index("    prior=W/'pg658-same-source-sixteen-native-v1'")
    end = raw.index("    host=W/", start)
    raw = raw[:start] + """    prior=W/'pg698-current-eight-native-v1';old=json.loads((prior/'manifest.safe.json').read_bytes())
    assert sha(prior/'manifest.safe.json')=='e55c6095a06be0e1aa5a316ee8e43663714728ed5527624e3223c30c1b2a4045'
    assert old['actualExit']==0 and old['productionSource']==SOURCE and old['currentNativeStreams']==8
    assert old['frozenHostManifestSha256']==HOST_SHA and len(old['singleSessions'])==len(old['selected'])==8
    assert all(type(s['sessions'])is int and s['sessions']==1 for s in old['singleSessions'])
    assert len({s['sessionIdSha256']for s in old['singleSessions']})==8
    assert all(m['classByteMismatch']==0 for m in old['moduleCounters'].values())
    first=prior;records=[old]
""" + raw[end:]
    return replace(raw, (
        ('from pg658_same_source_union import admissible\n', ''),
        ('zip((first,second),records)', 'zip((first,),records)'),
        ("'qualificationManifests':old['qualificationManifests']", "'qualificationManifests':{prior.name:sha(prior/'manifest.safe.json')}"),
    ))


if __name__ == '__main__':
    env = {'__name__': 'qualified_current9_only', '__file__': str(R / 'pg704_native.py')}
    exec(compile(source(), '<same source current eight plus actual ADMIN>', 'exec'), env)
    env['main']()
