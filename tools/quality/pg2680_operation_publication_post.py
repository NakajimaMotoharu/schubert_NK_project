"""Independent seven-phase current source publication; native preserved separately."""
import inspect
import json
from pyflakes.api import check
import pg2536_strict_normal_publication_post as previous
from pg1446_current_cold_stage import W
from pg2674_operation_publication_sources import candidate_bom,CURRENT,CURRENT_BOM,BEFORE,production

SLOT='pg2680-operation-publication-post-v1'


def compose(raw,receipt,fixed,bom):
    # Execute the complete independent contract in a new namespace with actual
    # current reader, source and candidate roles, not synthetic guest results.
    body=inspect.getsource(previous.compose)
    for a,b in [("save=base/'pg2514-current-cdbc-before-v2'","save=base/'pg2656-current-a79-before-v1'"),
      ('pg2514-current-cdbc-before-v2/native-before.private.json','pg2656-current-a79-before-v1/native-before.private.json'),
      ("/opt/schubert-nk/releases/0.1.0-PG2428","/opt/schubert-nk/releases/0.1.0-PG2512"),
      ("/opt/schubert-nk/releases/0.1.0-PG2512' and hashlib.sha256(manifest).hexdigest() == '\" + bom","/opt/schubert-nk/releases/0.1.0-PG2654' and hashlib.sha256(manifest).hexdigest() == '\" + bom"),
      ("str(base / 'pg2428-manifest.sig')","str(base / 'pg2512-manifest.sig')"),
      ("str(base / 'pg2512-manifest.sig')\")]:","str(base / 'pg2654-manifest.sig')\")]:"),
      (previous.SLOT,SLOT)]:body=body.replace(a,b)
    ns={**previous.__dict__,'TOOLS':'pg2674-operation-publication-tools-v1','SAVE':'pg2678-operation-publication-v1',
      'BEFORE':BEFORE,'CURRENT':CURRENT,'CURRENT_BOM':CURRENT_BOM,'production':production,'SLOT':SLOT}
    exec(compile(body,'<complete operation publication independent composer>','exec'),ns)
    result=ns['compose'](raw,receipt,fixed,bom)
    # PUBLIC_AFTER's oracle import name is a literal independent consumer.
    result=result.replace('pg2532_ordinary_publication_contract','pg2674_ordinary_publication_contract')
    if check(result,'<whole new operation publication post>'):raise ValueError('complete independent namespace required')
    compile(result,'<actual operation source publication post>','exec');return result


def payload():
    path=W/'pg2656-current-a79-before-v1/payload.private.py'
    receipt=json.loads((path.parent/'manifest.safe.json').read_bytes())
    fixed=json.loads((W/'pg2675-frozen-v1.safe.json').read_bytes())
    return compose(path.read_text(),receipt,fixed,candidate_bom())


def main():
    raw=inspect.getsource(previous.main).replace('pg2534-activate-v1.safe.json','pg2676-activate-v1.safe.json')
    ns={**previous.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<independent new seven-phase publication transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
