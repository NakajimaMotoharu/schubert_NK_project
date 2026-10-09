"""Independent new cohort's full-row seven-to-seven post oracle/capture sources."""
from pathlib import Path
from pg652_capture_retention import payload as previous_payload

R=Path(__file__).resolve().parent


def replace(raw,pairs):
    for old,new in pairs:
        assert old in raw,old;raw=raw.replace(old,new)
    return raw


def oracle():
    raw=(R/'pg652_retention_oracle.py').read_text()
    return replace(raw,(
        ('len(after)==514','len(after)==524'),('len(actual)==514','len(actual)==524'),
        ('len(before)==504','len(before)==514'),('len(prior)==504','len(prior)==514'),
        ("expected['eligibleUpperBound']==8 and expected['maximumEligibleAfterNew']==9", "expected['eligibleUpperBound']==7 and expected['maximumEligibleAfterNew']==8"),
        ("expected['expectedRetentionDeletes']==2", "expected['expectedRetentionDeletes']==1"),
        ('len(deleted)==2 and len(set(deleted))==2','len(deleted)==1 and len(set(deleted))==1'),
        ('len(removed)==10','len(removed)==5'),('b[5]==a[5]-1','b[5]==a[5]'),
        ("'oldRowsPreserved':504","'oldRowsPreserved':514"),("'retentionDeleted':2","'retentionDeleted':1"),
    ))


def capture():
    return replace(previous_payload(),(
        ('pg650-fresh-parent-v2','pg690-fresh-parent-v1'),
        ('pg652-retention-post-v2','pg692-retention-post-v1'),('PG652-retention-post-v2','PG692-retention-post-v1'),
        ('ef5312d0e59dbc9cce54d7c19eee35d2c7a2dc78afa325c404e4d2d108f73c22','c2a125086080538d44a434dd3313999d45d075a7debab2f103e984908707d982'),
        ('1826480','2146618'),('095f6d1d7f8442b7b2b44ae59a4314f5','6b3dd954959c43c1bbac2164ec9d0c6b'),
        ('111752','122726'),('107901545407','119288459330'),('==514','==524'),('<=514','<=524'),
        ('0.1.0-PG631','0.1.0-PG682'),
        ('57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe','076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480'),
        ('36fe7a0b938489d61d17d49c1c30a6fbbef699d5','9bd50536f692610036a0ed8b83e0a8b35fe2a66f'),
    ))
