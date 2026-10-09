"""Place unused signed715 only; current21/six private ADMIN trees stay unchanged."""
from pathlib import Path
from pg686_stage_candidate import source as previous
from pg662_sources import replace

R = Path(__file__).resolve().parent


def source():
    raw = replace(previous(), (
        ('pg686', 'pg718'), ('PG686', 'PG718'), ('pg682', 'pg715'), ('PG682', 'PG715'),
        ('0.1.0-PG631', '0.1.0-PG682'),
        ('9bd50536f692610036a0ed8b83e0a8b35fe2a66f', '1ec19782a1afe22d1de75b05f4cd12b8a8a8a172'),
        ('076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480', '74d35361865a32a6b992f93d78d42844e20a5bb286fa4fc4b5e74520fa6305d5'),
        ('57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe', '076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480'),
        ('pg684-completed-baseline-v2', 'pg716-completed-baseline-v1'),
        ('c039e70561fd7e5bab3ecf5ce204462d8415f4022d13793711c338a64d2f663d', '58154dc72379fc8a15c1d3098f75b571e14968819bec6901dfff594a6c78c029'),
        ("'/var/lib/pgpt-s1-preservation/pg664-bootstrap-existing-v1'", "'/var/lib/pgpt-s1-preservation/pg664-bootstrap-existing-v1','/var/lib/pgpt-s1-preservation/pg702-bootstrap-tools-v1','/var/lib/pgpt-s1-preservation/pg702-bootstrap-verify-v1','/var/lib/pgpt-s1-preservation/pg702-bootstrap-existing-v1'"),
        ('==514', '==524'),
    ))
    return raw


if __name__ == '__main__':
    env = {'__file__': str(R / 'pg718_stage_candidate.py'), '__name__': 'unused_candidate_only'}
    exec(compile(source(), '<signed unused715 without changing current>', 'exec'), env); env['main']()
