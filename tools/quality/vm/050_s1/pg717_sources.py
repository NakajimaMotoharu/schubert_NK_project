"""SSC233 new-only current21 completed deployment; both ADMIN cohorts stay immutable."""
import hashlib
from pathlib import Path
import pg685_sources as previous
from pg662_sources import replace

R = Path(__file__).resolve().parent
SOURCE = '1ec19782a1afe22d1de75b05f4cd12b8a8a8a172'
DIGEST = '74d35361865a32a6b992f93d78d42844e20a5bb286fa4fc4b5e74520fa6305d5'


def bind(raw):
    pairs = (
        ('pg685', 'pg717'), ('Pg685', 'Pg717'), ('PG685', 'PG717'),
        ('0.1.0-PG682', '0.1.0-PG715'), ('0.1.0-PG631', '0.1.0-PG682'),
        ('"PG682",source,NEXT', '"PG715",source,NEXT'),
        ('"PG631","36fe7a0b938489d61d17d49c1c30a6fbbef699d5",OLD', '"PG682","36fe7a0b938489d61d17d49c1c30a6fbbef699d5",OLD'),
        ('9bd50536f692610036a0ed8b83e0a8b35fe2a66f', SOURCE),
        ('36fe7a0b938489d61d17d49c1c30a6fbbef699d5', '9bd50536f692610036a0ed8b83e0a8b35fe2a66f'),
        ('076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480', DIGEST),
        ('57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe', '076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480'),
        ('601297d0-a8ba-47da-852b-0ffeae409965', '8633b77f-77dc-4a78-88b4-41165f159b43'),
        ('2026-10-08T21:33:23.332578Z', '2026-10-09T00:43:10.150245Z'),
        ('2026-10-08T21:33:23.332579Z', '2026-10-09T00:43:10.150246Z'),
        ('ad15ac4a-8d8e-4970-bcb3-2e000050ce77', 'c6815985-26c5-4f5f-aed0-abc81fa8f71e'),
        ('2026-10-08T22:03:10.738020Z', '2026-10-09T01:12:17.452418Z'),
        ('2026-10-08T22:03:10.738021Z', '2026-10-09T01:12:17.452419Z'),
        ('095f6d1d7f8442b7b2b44ae59a4314f5', '6b3dd954959c43c1bbac2164ec9d0c6b'),
        ('111752', '122726'), ('107901545407', '119288459330'), ('109694780700', '121040711116'),
        ('pg684-completed-baseline-v2', 'pg716-completed-baseline-v1'),
        ('c039e70561fd7e5bab3ecf5ce204462d8415f4022d13793711c338a64d2f663d', '58154dc72379fc8a15c1d3098f75b571e14968819bec6901dfff594a6c78c029'),
        ('pg655-native-stop-v1', 'pg696-native-stop-v1'), ('==514', '==524'),
    )
    return replace(raw, tuple((a, b) for a, b in pairs if a in raw))


def java(): return bind(previous.java())
def receipt(): return bind(previous.receipt())
def contract(): return bind(previous.contract())
def java_test(): return bind((R / 'Pg685CompletedDeploymentTest.java').read_text())


def refs():
    raw = bind(previous.refs())
    return replace(raw, (
        ('525e794cfd462b87a6000b4ad6e72dad4558dbe86fb2fbbb08d4791ffb975a9a', hashlib.sha256(receipt().encode()).hexdigest()),
        ("('pg664-bootstrap-tools-v1','pg664-bootstrap-verify-v1','pg664-bootstrap-existing-v1')",
         "('pg664-bootstrap-tools-v1','pg664-bootstrap-verify-v1','pg664-bootstrap-existing-v1','pg702-bootstrap-tools-v1','pg702-bootstrap-verify-v1','pg702-bootstrap-existing-v1')"),
    ))


def compile_script():
    raw = (R / 'pg685_compile_v2.sh').read_text().replace('pg685', 'pg717').replace('Pg685', 'Pg717').replace('PG685', 'PG717')
    return replace(raw, (
        ('pg717-completed-tools-v2', 'pg717-completed-tools-v1'),
        ('pg717-compile-v2', 'pg717-compile-v1'), ('pg717-oracle-v2', 'pg717-oracle-v1'),
        ('pg630-retention-factory-six-host-v1', 'pg680-owner-six-host-v1'),
        ('pg631-release-v1', 'pg682-release-v1'),
        ('test ! -e "$task_target"', 'test -d "$task_target"'),
        ('mkdir -m 700 "$task_target"', '# new-only output already created by pg717_compile'),
        ('tools/quality/vm/050_s1/Pg717CompletedDeployment.java tools/quality/vm/050_s1/Pg717CompletedDeploymentTest.java',
         '"$task_target/Pg717CompletedDeployment.java" "$task_target/Pg717CompletedDeploymentTest.java"'),
    ))
