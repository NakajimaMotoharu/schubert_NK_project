"""PG672 whole6 fresh qualification; 2 changed classes +3 abstract ports only."""
from pathlib import Path
import sys
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():
    raw=(R/'pg618_collect_candidate_full.py').read_text()
    raw=replace(raw,(
        ("'PG630': ('pg630-retention-factory-six-host-v1', 'pg628-retention-factory-component-v1',\n                  'e5ab539ed7e48de9889f6acbe28a8e2f71b3d20a633714ea6b548fc0ca3340b8',\n                  3468, 277, None)",
         "'PG630': ('pg672-entry-six-host-v1', 'pg670-entry-component-v1',\n                  'fec725f2f89945be5c88d5ef98a8446e155e7d701748a118191cdd2c8211f95b',\n                  3477, 277, None)"),
        ("old = W/('pg620-typed-oracle-six-host-v1'if selector=='PG630'else'pg599-candidate-bootstrap-six-host-v1')", "old = W/('pg630-retention-factory-six-host-v1'if selector=='PG630'else'pg599-candidate-bootstrap-six-host-v1')"),
        ('e83d2c34652b8c2bea5c1b9c02f00e9b757b88b5de6b1fb45e79b615ec003b57','067b8a155fe5a137aebb9c732bf800122752cb173ca8a09f3c41087d9efc178b'),
        ("selected_module = 'batch'if selector=='PG630'else'bootstrap'", "selected_module = 'api'if selector=='PG630'else'bootstrap'"),
        ('suites == 512 and total_classes == 1605','suites == 514 and total_classes == 1608'),
        ("'72fb7440697ee1048a5c0145055dc1cc3c577914'if selector=='PG630'", "'36fe7a0b938489d61d17d49c1c30a6fbbef699d5'if selector=='PG630'"),
    ))
    # Historical profile selector is internal; its output/run/source remain exactly PG672.
    return raw


if __name__=='__main__':
    assert len(sys.argv)==2
    env={'__name__':'frozen_current_collector','__file__':str(R/'pg673_collect_full.py')}
    exec(compile(source(),'<fresh entry source whole six>','exec'),env);env['main'](sys.argv[1],'PG630')
