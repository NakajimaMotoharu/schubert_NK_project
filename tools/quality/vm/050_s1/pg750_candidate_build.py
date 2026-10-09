"""New-only signed SSC234 fixed3513 host candidate; no guest mutation."""
from pathlib import Path
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():
    return replace((R/'pg682_candidate_build.py').read_text(),(
        ('pg682_candidate_contract','pg749_candidate_contract'),
        ('PG682','PG750'),('pg682','pg750'),('PG631','PG715'),('pg631-release-v1','pg715-release-v1'),
        ("SOURCE = '9bd50536f692610036a0ed8b83e0a8b35fe2a66f'","SOURCE = '8d4b68b4f1449932ebe506aaf08e584bbfea8dd2'"),
        ("OLD_SOURCE = '36fe7a0b938489d61d17d49c1c30a6fbbef699d5'","OLD_SOURCE = '1ec19782a1afe22d1de75b05f4cd12b8a8a8a172'"),
        ('pg680-owner-six-host-v1','pg748-closing-six-host-v1'),
        ('b710c69b798fcd14b35644541aed835689d81e6f0cbf40c3d67786e014f599e6','d4d3ba09651c75d15334e2775fa9a1ae8f8362e2fa92d9e8ebb57c1d8667d96e'),
        ('57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe','74d35361865a32a6b992f93d78d42844e20a5bb286fa4fc4b5e74520fa6305d5'),
        ('3489','3513'),('516','519'),('1612','1616'),("'changedClasses': 6","'changedClasses': 7"),
        ("'addedAbstractInterfaces': 7, 'addedInternalClasses': 0","'addedAbstractInterfaces': 1, 'addedInternalClasses': 1"),
    ))


if __name__=='__main__':
    exec(compile(source(),'<new signed finite closing candidate>', 'exec'),{'__file__':str(R/'pg750_candidate_build.py'),'__name__':'__main__'})
