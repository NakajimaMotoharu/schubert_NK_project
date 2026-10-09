"""Whitelist successful deployment receipts; retain misleading original count privately."""
from pathlib import Path
from pg688_public_current import R as OLD_R
from pg662_sources import replace

R = Path(__file__).resolve().parent


def source():
    raw = (OLD_R / 'pg688_public_current.py').read_text()
    return replace(raw, (
        ('PG685-687-current-public-v1', 'PG717-719-current-public-v1'),
        ('pg685-frozen-v4.safe.json', 'pg717-frozen-v1.safe.json'),
        ('pg685-stage-v1.safe.json', 'pg717-stage-v1.safe.json'),
        ('pg686-candidate-stage-v1.safe.json', 'pg718-candidate-stage-v1.safe.json'),
        ('pg685-verify-v1.safe.json', 'pg717-verify-v1.safe.json'),
        ('pg685-activate-v1.safe.json', 'pg717-activate-v1.safe.json'),
        ('pg687-activate-post-v1.safe.json', 'pg719-activate-post-v2.safe.json'),
        ("proof['batchRows']==514", "proof['batchRows']==524"),
        ('9bd50536f692610036a0ed8b83e0a8b35fe2a66f', '1ec19782a1afe22d1de75b05f4cd12b8a8a8a172'),
        ("'specifications':['555','556','557']", "'specifications':['577','578','579']"),
        ("'testIds':['FREEZE685001','PT-OPS-CODE685001','PT-OPS-CODE685002','PT-OPS-CODE685003','STAGE686001','STAGE686002','POST687001','POST687002']",
         "'testIds':['FREEZE717001','PT-OPS-CODE717001','PT-OPS-CODE717002','PT-OPS-CODE717003','STAGE718001','STAGE718002','POST719001','POST719002']"),
    ))


if __name__ == '__main__':
    exec(compile(source(), '<whitelist new six receipts>', 'exec'),
         {'__file__': str(R / 'pg720_public.py'), '__name__': '__main__'})
