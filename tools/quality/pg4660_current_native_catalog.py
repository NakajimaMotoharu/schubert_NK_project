"""Current Root ten physical native points; all58 prior copies stay data-only."""
import datetime
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
import pg2254_newboot_native_catalog as template
import pg4652_current_owned_sources as role
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg4152_exact_failed_done_recover import process

SLOT='pg4660-current-native-catalog-v1'
BOOT='79a3260a-e16d-42bf-942a-b914ed144c28'


ADMISSION=r'''
frozen_raw=(base/ONCE/'before.private.json').read_bytes();require(hashlib.sha256(frozen_raw).hexdigest()==BEFORE)
frozen=json.loads(frozen_raw)
require(set(frozen)=={'units','actors','database','flocks','durable','native','startup','runtime','configuration'}and len(frozen['database']['rows'])==24)
require(sum(pathlib.Path(p).suffix=='.exec'for p in frozen['native'])==58 and all(pathlib.Path(p).is_relative_to('/run/schubert-nk/pt-coverage')for p in frozen['native']))
issued=json.loads((base/ONCE/'external-start-guard.private.json').read_bytes())
require(issued['source']==CURRENT_SOURCE and issued['manifestSha256']==CURRENT_BOM and issued['ordinaryNoargs']is True and issued['oldRunNotResumed']is True and issued['originalBudgetSeconds']==1800 and issued['attemptReserved']is True and issued['replayAllowed']is False)
old=json.loads((base/ONCE/'native-before-manifest.private.json').read_bytes());require(len(old)==58)
for relative,item in old.items():
 require(not pathlib.PurePosixPath(relative).is_absolute()and '..'not in pathlib.PurePosixPath(relative).parts)
 p=base/ONCE/'native-before-private'/relative;s=p.lstat()
 require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(p))
 blob=p.read_bytes();archive_record(item,blob);require(meta(s)==meta(p.lstat()))
 original=frozen['native']['/run/schubert-nk/pt-coverage/'+relative]
 require(original['sha256']==item['sha256']and original['metadata'][6]==item['bytes'])
'''


def catalog_source(receipt,binding,end):
    # Generate the positive catalog body separately; never rewrite its independent
    # parent receipt, including negative vectors or historical immutable capsules.
    stub='def completed(*args):raise ValueError("body-only; never executed")'
    raw=template.catalog_source(stub,binding,end)
    if not raw.startswith(stub+'\n'):raise ValueError('one body-only boundary')
    raw=raw[len(stub)+1:]
    first=raw.index('frozen=json.loads(');last=raw.index('native=pathlib.Path',first)
    raw=raw[:first]+ADMISSION+raw[last:]
    for old,new in [(template.BOOT,BOOT),(template.BOOT.replace('-',''),BOOT.replace('-','')),('pg2246','pg4652')]:raw=raw.replace(old,new)
    raw=raw.replace("'currentBootHadNoHistoricalNative':True","'all58BeforeCopiesPreserved':True,'oldSourceNativeImported':False")
    header='import os\nONCE='+repr(role.admission.ONCE)+'\nBEFORE='+repr(role.admission.before())+'\nCURRENT_SOURCE='+repr(role.SOURCE)+'\nCURRENT_BOM='+repr(role.BOM)+'\n'
    result=receipt+'\n'+header+raw
    if check('SEALS={}\n'+result,'<same964e ten actual native points>'):raise ValueError('complete actual native globals')
    return result


def prerequisites(post,terminal):
    if not(post.get('actualExit')==0 and post.get('productionSource')==role.SOURCE and post.get('allClientAdvisoryFlock0')is True and post.get('all24UnchangedTwice')is True and post.get('allTenUnitsKernelEmpty')is True and post.get('normalNewMetadataScopes')is True and terminal.get('productionSource')==role.SOURCE and terminal.get('genuineRootDone')is True and terminal.get('completionCode')==10):raise ValueError('actual current normal Root/independent full stop post first')


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed native reader first')
    post=json.loads((W/'pg4658-current-owned-post-v1/manifest.safe.json').read_bytes());terminal=role.actual.receipt(role.acceptance.TERM);prerequisites(post,terminal)
    receipt=(W/role.TOOLS/'pg4652_parent_receipt.py').read_text()
    seals={n:post['proofHashes'][n]['sha256']for n in ['before.private.json','after.private.json','complete.private','parent.private.jsonl']}
    raw='SEALS='+repr(seals)+'\n'+catalog_source(receipt,role.admission.live(),terminal['endMonotonicUs'])
    role.admission.authenticate_host();os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);(out/'payload.private.py').write_text(raw)
    with management_gate(P/'current-management-critical.lock'):
        with(out/'stdout.private.log').open('xb')as output,(out/'stderr.private.log').open('xb')as error:
            child=subprocess.Popen(SSH+['sudo','-n','python3','-B','-'],stdin=subprocess.PIPE,stdout=output,stderr=error)
            (out/'start.safe.json').write_text(json.dumps({'owner':process(os.getpid()),'ssh':process(child.pid),'source':role.SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'replayAllowed':False}))
            child.stdin.write(raw.encode());child.stdin.close();code=child.wait();output.flush();error.flush();os.fsync(output.fileno());os.fsync(error.fileno())
    value={'actualExit':code,'productionSource':role.SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'formalAccepted':False}
    if code==0:value.update(json.loads((out/'stdout.private.log').read_bytes()))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k not in ['selected','excludedHistorical']}));return code


if __name__=='__main__':raise SystemExit(main())
