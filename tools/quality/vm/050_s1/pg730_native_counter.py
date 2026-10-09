"""Only current55ac eight native streams, exact PG713 host; no9bd streams imported."""
from pathlib import Path
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():
    return replace((R/'pg698_native_counter.py').read_text(), (
        ('pg698','pg730'),('PG698','PG730'),('pg696','pg728'),('pg697','pg729'),('pg693','pg725'),
        ('9bd50536f692610036a0ed8b83e0a8b35fe2a66f','1ec19782a1afe22d1de75b05f4cd12b8a8a8a172'),
        ('8633b77f-77dc-4a78-88b4-41165f159b43','55ac70e7-0180-4c32-8c91-5a379ebedf24'),
        ('119288459330','127549297774'),('121088459330','129349297774'),
        ('122726','132812'),('6b3dd954959c43c1bbac2164ec9d0c6b','2aff8ecf3b7d4d15b24a8af0f73a8745'),
        ('pg680-owner-six-host-v1','pg713-expiry-six-host-v1'),
        ('b710c69b798fcd14b35644541aed835689d81e6f0cbf40c3d67786e014f599e6','5f6a57015fb30d8f2097e594370d558ac6202a9d5d2ed98ce0108494cc7f524a'),
        ("tests']==3489","tests']==3502"),
    ))


def namespace():
    env={'__file__':str(R/'pg730_native_counter.py'),'__name__':'current_source_native_only'}
    exec(compile(source(),'<exact current eight native qualification>','exec'),env)
    return env


def code(hashes,proof,seals):
    assert type(proof)is dict and type(proof.get('actualExit'))is int and proof['actualExit']==0
    assert proof['genuineCompletion']['genuineRootDone']is True and proof['genuineCompletion']['genuinePid1StartDone']is True
    return namespace()['code'](hashes,proof,seals)
def catalog(before_sha):return namespace()['catalog'](before_sha)


if __name__=='__main__':
    env=namespace()
    previous_code=env['code']
    def strict_code(hashes,proof,seals):
        assert type(proof)is dict and type(proof.get('actualExit'))is int and proof['actualExit']==0
        assert proof['genuineCompletion']['genuineRootDone']is True and proof['genuineCompletion']['genuinePid1StartDone']is True
        return previous_code(hashes,proof,seals)
    env['code']=strict_code;env['main']()
