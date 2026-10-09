"""New signed PG713 candidate; exact current PG682 is retained, guest mutations0."""
from pathlib import Path
from pg662_sources import replace

R = Path(__file__).resolve().parent


def source():
    raw = (R / 'pg682_candidate_build.py').read_text()
    raw = replace(raw, (
        ('pg682_candidate_contract', 'pg715_candidate_contract'),
        ('pg682-release-v1', 'pg715-release-v1'), ('pg682-manifest-v1.sig', 'pg715-manifest-v1.sig'),
        ('pg682-sign-v1', 'pg715-sign-v1'), ('pg682-candidate-build-v1', 'pg715-candidate-build-v1'),
        ('PG682', 'PG715'), ('PG631', 'PG682'), ('pg631-release-v1', 'pg682-release-v1'),
        ("SOURCE = '9bd50536f692610036a0ed8b83e0a8b35fe2a66f'", "SOURCE = '1ec19782a1afe22d1de75b05f4cd12b8a8a8a172'"),
        ("OLD_SOURCE = '36fe7a0b938489d61d17d49c1c30a6fbbef699d5'", "OLD_SOURCE = '9bd50536f692610036a0ed8b83e0a8b35fe2a66f'"),
        ('pg680-owner-six-host-v1', 'pg713-expiry-six-host-v1'),
        ('b710c69b798fcd14b35644541aed835689d81e6f0cbf40c3d67786e014f599e6', '5f6a57015fb30d8f2097e594370d558ac6202a9d5d2ed98ce0108494cc7f524a'),
        ('57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe', '076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480'),
        ('3489', '3502'), ('516', '517'), ('1612', '1614'),
        ("'changedClasses': 6", "'changedClasses': 1"),
        ("'addedAbstractInterfaces': 7, 'addedInternalClasses': 0", "'addedAbstractInterfaces': 1, 'addedInternalClasses': 1"),
        ("{'VERSION', 'api/api.jar'} <= changed", "{'VERSION', 'operations/batch.jar'} <= changed"),
    ))
    return raw


if __name__ == '__main__':
    exec(compile(source(), '<new signed Expiry current candidate>', 'exec'),
         {'__file__': str(R / 'pg715_candidate_build.py'), '__name__': '__main__'})
