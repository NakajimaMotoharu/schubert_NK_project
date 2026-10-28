"""Finite typed metadata normalization: fresh duplicates, stale project coordinates and externals differ."""

def normalize(fresh,roots,dependencies):
    assert len(fresh) == len(set(fresh)) == len(roots) == len(set(roots)) == 6
    assert not set(fresh)&set(roots)
    roles = ['api','batch','bootstrap','protocol','storage','web'];external = set();old = set();reused = set()
    for value in dependencies:
        if value in fresh:reused.add(value)
        elif '/dev/codex/schubert/schubert-nk-' in value:
            assert any('/dev/codex/schubert/schubert-nk-'+role+'/' in value for role in roles)
            old.add(value)
        else:
            # A different fresh project JAR path is not silently treated as external.
            assert not any(value.endswith('/schubert-nk-'+role+'-0.1.0-SNAPSHOT.jar') for role in roles)
            external.add(value)
    result = [*fresh,*roots,*sorted(external)]
    assert len(result) == len(set(result)) and not set(result)&old
    return result,sorted(external),sorted(old),sorted(reused)

def selftest():
    roles = ['api','batch','bootstrap','protocol','storage','web']
    fresh = ['/owned/'+role+'/schubert-nk-'+role+'-0.1.0-SNAPSHOT.jar' for role in roles]
    roots = ['/owned/'+role+'/test-classes' for role in roles]
    old = '/repo/dev/codex/schubert/schubert-nk-api/0.1.0-SNAPSHOT/schubert-nk-api-0.1.0-SNAPSHOT.jar'
    value,external,stale,reused = normalize(fresh,roots,[fresh[0],fresh[0],old,'/external/a.jar','/external/a.jar'])
    assert value == [*fresh,*roots,'/external/a.jar'] and external == ['/external/a.jar'] and stale == [old] and reused == [fresh[0]]
    rejected = 0
    for a,b,c in [(fresh+fresh[:1],roots,[]),(fresh,roots+roots[:1],[]),
        (fresh,roots,['/repo/dev/codex/schubert/schubert-nk-unknown/1/a.jar']),
        (fresh,roots,['/foreign/api/schubert-nk-api-0.1.0-SNAPSHOT.jar'])]:
        try:normalize(a,b,c)
        except AssertionError:rejected += 1
        else:raise AssertionError('ambiguous or duplicate static scope accepted')
    return dict(positive=1,negative=rejected)
