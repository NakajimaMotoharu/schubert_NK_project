"""Exact current parent independently validates534 rows,524 original and one retention."""
from pg692_retention_sources import oracle as previous_oracle, capture as previous_capture
from pg662_sources import replace


def bind(raw):
    return replace(raw, tuple((a,b) for a,b in (
        ('pg690','pg722'), ('pg691','pg723'), ('pg692','pg724'), ('PG692','PG724'),
        ('c2a125086080538d44a434dd3313999d45d075a7debab2f103e984908707d982','96a45c46a3e3f33924331fdebfb716bf1a47581b9eb3765f1a00eb4a8d09514e'),
        ('2146618','2468821'), ('6b3dd954959c43c1bbac2164ec9d0c6b','2aff8ecf3b7d4d15b24a8af0f73a8745'),
        ('122726','132812'), ('119288459330','127549297774'),
        ('0.1.0-PG682','0.1.0-PG715'),
        ('9bd50536f692610036a0ed8b83e0a8b35fe2a66f','1ec19782a1afe22d1de75b05f4cd12b8a8a8a172'),
        ('076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480','74d35361865a32a6b992f93d78d42844e20a5bb286fa4fc4b5e74520fa6305d5'),
    ) if a in raw))


def oracle():
    return replace(previous_oracle(), (
        ('len(after)==524','len(after)==534'), ('len(actual)==524','len(actual)==534'),
        ('len(before)==514','len(before)==524'), ('len(prior)==514','len(prior)==524'),
        ("'oldRowsPreserved':514","'oldRowsPreserved':524"),
    ))


def capture():
    return replace(bind(previous_capture()), (('==524','==534'),('<=524','<=534')))
