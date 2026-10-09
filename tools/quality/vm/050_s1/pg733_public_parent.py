"""Future successful current campaign whitelist only; run after exact native qualification."""
from pathlib import Path
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():
    return replace((R/'pg699_public_parent.py').read_text(), (
        ('pg689','pg721'),('pg690','pg722'),('PG690','PG722'),('pg692','pg724'),
        ('pg693','pg725'),('pg694','pg726'),('pg696','pg728'),('pg697','pg729'),('pg698','pg730'),
        ('9bd50536f692610036a0ed8b83e0a8b35fe2a66f','1ec19782a1afe22d1de75b05f4cd12b8a8a8a172'),
        ("'specs':['558','559','560','561','562','563','564','565']","'specs':['580','581','582']"),
        ("'testIds':['BACK689001','FRESH690001..004','RET692001..002','DONE693001..002','A01-694001..002','STOP696001..003','POST697001..002','NATIVE698001..002']",
         "'testIds':['PRES721001','ORD722001','ORD722002','OBS723001','RET724001','DONE725001','CHR726001','STOP728001','STOP728002','POST729001','NAT730001']"),
    ))


if __name__=='__main__':
    exec(compile(source(),'<whitelisted new current parent results>','exec'),
         {'__file__':str(R/'pg733_public_parent.py'),'__name__':'__main__'})
