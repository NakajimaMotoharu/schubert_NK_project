"""New-only SSC234 candidate completed21 binding; current751/nine private trees unchanged."""
import hashlib
from pathlib import Path
import pg717_sources as previous
from pg662_sources import replace

R=Path(__file__).resolve().parent
SOURCE='8d4b68b4f1449932ebe506aaf08e584bbfea8dd2'
DIGEST='a96ddf6542dff9cdecfb9f92b48c4cefec5c5299598d47e0ce54ad98e5231289'


def bind(raw):
    pairs=(
        ('pg717','pg752'),('Pg717','Pg752'),('PG717','PG752'),
        ('0.1.0-PG715','NEXT_RELEASE_752'),('0.1.0-PG682','0.1.0-PG715'),('NEXT_RELEASE_752','0.1.0-PG750'),
        ('"PG715",source,NEXT','"PG750",source,NEXT'),
        ('"PG682","9bd50536f692610036a0ed8b83e0a8b35fe2a66f",OLD','"PG715","9bd50536f692610036a0ed8b83e0a8b35fe2a66f",OLD'),
        ('1ec19782a1afe22d1de75b05f4cd12b8a8a8a172','NEXT_SOURCE_752'),
        ('9bd50536f692610036a0ed8b83e0a8b35fe2a66f','1ec19782a1afe22d1de75b05f4cd12b8a8a8a172'),('NEXT_SOURCE_752',SOURCE),
        ('74d35361865a32a6b992f93d78d42844e20a5bb286fa4fc4b5e74520fa6305d5','NEXT_BOM_752'),
        ('076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480','74d35361865a32a6b992f93d78d42844e20a5bb286fa4fc4b5e74520fa6305d5'),('NEXT_BOM_752',DIGEST),
        ('8633b77f-77dc-4a78-88b4-41165f159b43','55ac70e7-0180-4c32-8c91-5a379ebedf24'),
        ('2026-10-09T00:43:10.150245Z','2026-10-09T03:00:51.014287Z'),
        ('2026-10-09T00:43:10.150246Z','2026-10-09T03:00:51.014288Z'),
        ('c6815985-26c5-4f5f-aed0-abc81fa8f71e','ab8895ca-4fb1-440d-b174-bc9f1f27505a'),
        ('2026-10-09T01:12:17.452418Z','2026-10-09T03:30:40.608594Z'),
        ('2026-10-09T01:12:17.452419Z','2026-10-09T03:30:40.608595Z'),
        ('6b3dd954959c43c1bbac2164ec9d0c6b','2aff8ecf3b7d4d15b24a8af0f73a8745'),
        ('122726','132812'),('119288459330','127549297774'),('121040711116','129343844863'),
        ('pg716-completed-baseline-v1','pg751-completed-baseline-v1'),
        ('58154dc72379fc8a15c1d3098f75b571e14968819bec6901dfff594a6c78c029','8c722e15a3bc9b6e311fe69cef0cd2aa3a954e87586c861cafa7279cd3dab6c0'),
        ('pg696-native-stop-v1','pg728-native-stop-v1'),('==524','==534'),
        ("('pg664-bootstrap-tools-v1','pg664-bootstrap-verify-v1','pg664-bootstrap-existing-v1','pg702-bootstrap-tools-v1','pg702-bootstrap-verify-v1','pg702-bootstrap-existing-v1')",
         "('pg664-bootstrap-tools-v1','pg664-bootstrap-verify-v1','pg664-bootstrap-existing-v1','pg702-bootstrap-tools-v1','pg702-bootstrap-verify-v1','pg702-bootstrap-existing-v1','pg737-bootstrap-tools-v1','pg737-bootstrap-verify-v1','pg737-bootstrap-existing-v1')"),
    )
    # BUG926: restoration markers are created by prior pairs, never filter on initial raw.
    for old,new in pairs:
        if old in raw:raw=raw.replace(old,new)
    for marker in ('NEXT_RELEASE_752','NEXT_SOURCE_752','NEXT_BOM_752'):
        if marker in raw:raise ValueError('unrestored candidate binding')
    return raw.replace('pg752-completed-tools-v1','pg752-completed-tools-v2')


def java():return bind(previous.java())
def receipt():return bind(previous.receipt())
def contract():return bind(previous.contract())
def java_test():return bind(previous.java_test())


def refs():
    raw=bind(previous.refs())
    return replace(raw,((hashlib.sha256(previous.receipt().encode()).hexdigest(),hashlib.sha256(receipt().encode()).hexdigest()),))


def compile_script():
    return replace(bind(previous.compile_script()),(
        ('pg680-owner-six-host-v1','pg713-expiry-six-host-v1'),('pg682-release-v1','pg715-release-v1'),
    ))
