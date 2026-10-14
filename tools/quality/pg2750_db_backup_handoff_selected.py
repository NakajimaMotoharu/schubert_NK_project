"""Actual isolated PostgreSQL handoff-boundary PT, immutable current Main/current native only."""
import inspect
import json
from pyflakes.api import check
import pg2292_morning_guard_selected as database
import pg2220_root_uid_host_selected as transport
from pg2674_operation_publication_sources import production

SOURCE=production()
FILES=[database.FILES[0],'tools/quality/vm/050_s1/Pg2750BackupHandoffLauncher.java',*database.FILES[2:]]


def native_input():
    W=transport.W
    receipt=json.loads((W/'pg2746-backup-admission-native-qualified-v2/manifest.safe.json').read_bytes())
    original=json.loads((W/'pg2722-operation-native-qualified-v1/input.safe.json').read_bytes())
    full=json.loads((W/'pg2745-backup-admission-full-qualified-v1/manifest.safe.json').read_bytes())
    result=receipt['result']
    if any(type(x.get('actualExit'))is not int or x['actualExit']!=0 for x in [receipt,full]):raise ValueError('actual full/native required')
    if receipt.get('productionSource')!=SOURCE or original.get('productionSource')!=SOURCE or result['classByteMismatch']!=0 or result['qualified2744Tests']!=3669 or full['result']['tests']!=3669 or result['all1643MainMembersIdentical']!=1643 or result['oldNativeImported']is not False:
        raise ValueError('ownsource latest nine full-byte qualification required')
    files={str(i)+'.exec':v['sha256']for i,v in enumerate(original['selected'])if not(v['unit']=='schubert-nk-inbox-inspector.service'and v['relative'].endswith('.terminal.exec'))}
    if len(files)!=9:raise ValueError('exact latest-closing only nine streams required')
    return {'manifestSha256':receipt['manifestSha256'],'files':files}


def server():
    raw=database.server()
    for before,after in [('PG2292','PG2750'),('Pg2292MorningGuardLauncher','Pg2750BackupHandoffLauncher'),
                         ('source-full-PG2228','source-full-PG2744'),('PG2284-native-v1','PG2746-native-v2'),
                         ('tests2 failures0','tests1 failures0'),("'tests':'2'","'tests':'1'"),
                         ("len(x.findall('testcase'))==2","len(x.findall('testcase'))==1"),("'tests':2","'tests':1")]:
        if before not in raw:raise ValueError('exact immutable selected namespace boundary required')
        raw=raw.replace(before,after)
    if check('INPUT={}\n'+raw,'<current DB handoff server>'):raise ValueError('complete namespace required')
    compile(raw,'<isolated actual DB handoff boundary>','exec');return raw


def main():
    raw=inspect.getsource(transport.main).replace('PG2220','PG2750').replace('pg2220','pg2750').replace(
        'pg2125-metadata-boundary-full-qualified-v1','pg2745-backup-admission-full-qualified-v1')
    raw=raw.replace(",'libraries':libs}",",'libraries':libs,'native':native_input()}")
    ns={**transport.__dict__,'SOURCE':SOURCE,'FILES':FILES,'SLOT':'pg2750-db-backup-handoff-selected-v1','SERVER':server(),'native_input':native_input}
    exec(compile(raw,'<fixed current isolated DB selection>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
