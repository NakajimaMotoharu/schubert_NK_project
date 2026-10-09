"""Fresh current PG715 full21 after owned728, immutable six old ADMIN private trees."""
from pathlib import Path
from pg701_current_baseline import source as previous
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():
    return replace(previous(), (
        ('pg701-completed-baseline-v1','pg736-completed-baseline-v1'),
        ('pg696-native-stop-v1','pg728-native-stop-v1'),
        ('97ac29b61037e24f78cd730b229a2a720363b3b2b5f51fd39ddc504dfad40516','3dc7e756a77c066f53c7503f8109564c559475ffda98e157c1eb2b0ee62e5c32'),
        ('6b3dd954959c43c1bbac2164ec9d0c6b','2aff8ecf3b7d4d15b24a8af0f73a8745'),
        ('PG682','PG715'),
        ('076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480','74d35361865a32a6b992f93d78d42844e20a5bb286fa4fc4b5e74520fa6305d5'),
        ('9bd50536f692610036a0ed8b83e0a8b35fe2a66f','1ec19782a1afe22d1de75b05f4cd12b8a8a8a172'),
        ('==524','==534'),("'batchRows':524","'batchRows':534"),
        ("('pg664-bootstrap-tools-v1','pg664-bootstrap-verify-v1','pg664-bootstrap-existing-v1')",
         "('pg664-bootstrap-tools-v1','pg664-bootstrap-verify-v1','pg664-bootstrap-existing-v1','pg702-bootstrap-tools-v1','pg702-bootstrap-verify-v1','pg702-bootstrap-existing-v1')"),
        ("(W/'pg697-terminal-final-v1.exit')","(W/'pg729-terminal-final-v1.exit')"),
    ))


if __name__=='__main__':
    exec(compile(source(),'<fresh current full21 readonly>','exec'),
         {'__file__':str(R/'pg736_current_baseline.py'),'__name__':'__main__'})
