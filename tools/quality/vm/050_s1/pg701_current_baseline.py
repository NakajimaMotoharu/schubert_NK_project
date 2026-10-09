"""Fresh current source9bd completed21 readonly baseline, no operation authority."""
from pathlib import Path
from pg661_current_baseline import source as previous
from pg692_retention_sources import replace

R=Path(__file__).resolve().parent


def source():
    return replace(previous(),(
        ('pg661-completed-baseline-v1','pg701-completed-baseline-v1'),
        ('pg655-native-stop-v1','pg696-native-stop-v1'),
        ('c13792efb16007ad6fbdcec310dc9c8a598d9a5bad1b4680bef93384ab092285','97ac29b61037e24f78cd730b229a2a720363b3b2b5f51fd39ddc504dfad40516'),
        ('095f6d1d7f8442b7b2b44ae59a4314f5','6b3dd954959c43c1bbac2164ec9d0c6b'),
        ('0.1.0-PG631','0.1.0-PG682'),
        ('57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe','076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480'),
        ('36fe7a0b938489d61d17d49c1c30a6fbbef699d5','9bd50536f692610036a0ed8b83e0a8b35fe2a66f'),
        ('==514','==524'),("'batchRows':514","'batchRows':524"),
        ('require(len(v)==20);return v',"v['currentBootstrapProofs']={n:tree(base/n)for n in ('pg664-bootstrap-tools-v1','pg664-bootstrap-verify-v1','pg664-bootstrap-existing-v1')}\n  require(len(v)==21);return v"),
        ("'full20Fields':True", "'full21Fields':True,'currentBootstrapPrivateProofsPreserved':True"),
        ("(W/'pg656-terminal-final-v1.exit')", "(W/'pg697-terminal-final-v1.exit')"),
    ))


if __name__=='__main__':
    exec(compile(source(),'<fresh completed current21 readonly>','exec'),
         {'__file__':str(R/'pg701_current_baseline.py'),'__name__':'__main__'})
