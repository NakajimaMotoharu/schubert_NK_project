"""Current fresh-day whole seal; independent terminal/all24/source/four owners, read-only."""
import inspect
import json
from pyflakes.api import check
import pg2186_newsource_full_live_seal as prior
from pg2234_newboot_fresh_day_terminal import payload as terminal_payload,SLOT as TERM
from pg2240_newboot_fresh_day_rows import oracle_source
from pg2025_fresh_resume_full_live_seal import constant
from pg1446_current_cold_stage import W
from pg2208_current_newboot_cold_sources import BOOT

SLOT='pg2242-newboot-fresh-day-full-seal-v1'


def normalize_frozen(frozen):
    if type(frozen)is not dict or set(frozen)!={'current','runtime','systemdRuntime','ordinaryNoargs','newJstDate','existingSuccessfulInspectorStepsForDate','availableBytes','requiredGuestWriteAndCloseBytes'}:
        raise ValueError('exact current fresh admission schema required')
    v=frozen['current']
    if type(v)is not dict or set(v)!={'boot','source','manifestSha256','units','configuration','rows','durable','unitFiles','maintenance'} or v['boot']!=BOOT or v['source']!=prior.SOURCE or v['manifestSha256']!=prior.BOM:
        raise ValueError('complete current boot image required')
    if set(v['durable'])!={'backup','originals','credentials','oldProofs'} or len(v['units'])!=10 or len(v['rows'])!=24:
        raise ValueError('whole ten/24/durable image required')
    if frozen['ordinaryNoargs']is not True or frozen['existingSuccessfulInspectorStepsForDate']!=0:
        raise ValueError('qualified fresh day required')
    return {'backup':v['durable']['backup'],'originals':v['durable']['originals'],
      'extraDurable':{k:v['durable'][k]for k in ['credentials','oldProofs']},'configuration':v['configuration'],
      'rows':v['rows'],'units':v['units'],'runtime':frozen['systemdRuntime'],
      'unitFilesActual':{p:x['metadata']+[x['sha256']]for p,x in v['unitFiles'].items()}}


def payload(binding,before_sha,oracle_sha):
    raw=prior.payload(binding).replace(prior.SLOT,SLOT).replace('3d69f5af-6bac-46b1-a540-7591c4a79a0d',BOOT)
    raw=raw.replace('pg2178-newsource-noargs-once-v1','pg2227-newboot-fresh-day-once-v1').replace(prior.BEFORE,before_sha)
    raw=raw.replace('2026-10-13T06:29:34.698736Z',binding['cutoff']).replace('02bddddf-9cd3-4668-9d67-7561232fc4e4',binding['run']).replace('20b86040-ffd5-4d17-9fca-5d83048ba905',binding['activation'])
    marker='before=json.loads(before_raw)'
    if raw.count(marker)!=1:raise ValueError('one actual sealed admission image required')
    start=raw.index('def before_shape(before):');end=raw.index("before['durable']=",start)
    raw=raw[:start]+raw[end:]
    raw=raw.replace(marker,'\n'+inspect.getsource(normalize_frozen)+'\nbefore=normalize_frozen(json.loads(before_raw))')
    raw=raw.replace('v[\'source\']!=prior.SOURCE','v[\'source\']!=SOURCE').replace('v[\'manifestSha256\']!=prior.BOM','v[\'manifestSha256\']!=BOM')
    guard=terminal_payload(binding);point="out=pathlib.Path('/var/lib/pgpt-s1-preservation/"+TERM+"')"
    raw=constant(raw,'GUARD',guard[:guard.index(point)])
    oracle=oracle_source().replace('def qualify(before,now,oracle,run,cutoff,upper):','def qualify_day(before,now,oracle,run,cutoff,upper):')
    oracle+='\nimport hashlib,pathlib\nORAW=pathlib.Path(\'/var/lib/pgpt-s1-preservation/pg2238-newboot-before-selectors-v1/oracle.private.json\').read_bytes()\nrequire(hashlib.sha256(ORAW).hexdigest()=='+repr(oracle_sha)+')\nDAY_ORACLE=json.loads(ORAW)\n'
    oracle+='\ndef qualify(old,new,cutoff,done,upper):\n    require(instant(cutoff)<=instant(done)<=instant(upper))\n    require(DAY_ORACLE[\'beforeSha256\']=='+repr(before_sha)+' and DAY_ORACLE[\'cutoff\']==cutoff)\n    return qualify_day(old,new,DAY_ORACLE,'+repr(binding['run'])+',cutoff,upper)\n'
    raw=constant(raw,'ORACLE',oracle)
    if check(raw,'<actual current fresh-day whole seal>'):raise ValueError('whole fullseal exports required')
    compile(raw,'<current fresh-day full seal>','exec');return raw


def main():
    before=json.loads((W/'pg2226-newboot-fresh-day-before-v1/manifest.safe.json').read_bytes())
    oracle=json.loads((W/'pg2238-newboot-before-selectors-v1/manifest.safe.json').read_bytes())
    if before['actualExit']!=0 or oracle['actualExit']!=0:raise ValueError('actual fresh before and independent oracle required')
    raw=inspect.getsource(prior.prior.previous.previous.main)
    for old,new in [('pg2021-fresh-resume-terminal-receipt-v1',TERM),('pg2023-fresh-resume-rows-oracle-v1','pg2240-newboot-fresh-day-rows-v1'),('pg2019-fresh-resume-live-binding-complete-v1','pg2230-newboot-current-live-binding-v1')]:raw=raw.replace(old,new)
    raw=raw.replace("payload(live['binding'])","payload({**live['binding'],'rootPid':live['rootPid']},before['guest']['privateBeforeSha256'],oracle['guest']['privateOracleSha256'])")
    ns={**prior.prior.previous.previous.__dict__,'SLOT':SLOT,'SOURCE':prior.SOURCE,'payload':payload,'before':before,'oracle':oracle}
    exec(compile(raw,'<actual newboot current full seal transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
