"""Current-only stage/verify/one existingADMIN execution; no Morning/replay."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'vm/050_s1'))
from pg986_current_bootstrap_native import source as previous
from pg1719_current_bootstrap_sources import bind


def source():
    raw=bind(previous())
    raw=raw.replace('pg1719-frozen-v3.safe.json','pg1720-frozen-v1.safe.json')
    raw=raw.replace('pg1719-fixed-stage-v3','pg1721-fixed-stage-v1')
    raw=raw.replace("'pg1719-'+action+'-v3'","'pg1721-'+action+'-v1'")
    raw=raw.replace('pg1719-stage-v3.exit','pg1721-stage-v1.exit')
    raw=raw.replace('pg1719-verify-v3.exit','pg1721-verify-v1.exit')
    start=raw.index("    assert(W/'pg1703-stop-v1.exit')")
    end=raw.index('    frozen=',start)
    raw=raw[:start]+"""    before=json.loads((W/'pg1718-current-bootstrap-before-v1/manifest.safe.json').read_bytes())
    done=json.loads((W/'pg1701-new-source-done-receipt-v1.safe.json').read_bytes())
    post=json.loads((W/'pg1707-new-source-terminal-post-v1.safe.json').read_bytes())
    assert before['actualExit']==done['actualExit']==post['actualExit']==0
    assert before['productionSource']==done['source']==post['productionSource']=='2741c4546afad6c1e8b6efbd53dfb58144edf7bb'
    assert before['beforeSha256']=='6b29aa3fbeee305335bba17f2fe40f51041a3197cc17c9795a9ddd949930c838'and post['allClientAdvisoryFlock0']is True
    assert done['receipt']['endMonotonicUs']==68542820690 and done['receipt']['genuineRootDone']is True
    if action=='execute':assert(W/'pg1721-verify-v1.exit').read_bytes()==b'0\\n'
"""+raw[end:]
    raw=raw.replace("assert type(frozen['actualExit'])is int and frozen['actualExit']==0",
                    "assert type(frozen['actualExit'])is int and frozen['actualExit']==0 and frozen['productionSource']==before['productionSource']and frozen['beforeSha256']==before['beforeSha256']")
    compile(raw,'<current Bootstrap immutable stage and once execution>','exec')
    return raw


def main():
    if sys.argv[1:]not in (['stage'],['verify'],['execute']):raise ValueError('exact three Bootstrap phases required')
    ns={'__file__':str(Path(__file__).parent/'vm/050_s1/pg1721_current_bootstrap_dispatch.py'),'__name__':'current_bootstrap_dispatch'}
    exec(compile(source(),'<current Bootstrap transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
