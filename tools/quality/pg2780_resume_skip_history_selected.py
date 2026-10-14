"""Actual DB resume skips cannot be authorized from foreign JDBC history; current frozen Main."""
import inspect
import json
import pg2750_db_backup_handoff_selected as previous

SOURCE=previous.SOURCE
FILES=[previous.FILES[0],'tools/quality/vm/050_s1/Pg2780ResumeSkippedLauncher.java',*previous.FILES[2:]]


def native_input():
    W=previous.transport.W
    receipt=json.loads((W/'pg2774-db-contract-native-qualified-v1/manifest.safe.json').read_bytes())
    original=json.loads((W/'pg2722-operation-native-qualified-v1/input.safe.json').read_bytes())
    full=json.loads((W/'pg2772-db-contract-full-qualified-v1/manifest.safe.json').read_bytes())
    r=receipt['result']
    if any(type(v.get('actualExit'))is not int or v['actualExit']!=0 for v in [receipt,full]):raise ValueError('actual whole/current native required')
    if receipt.get('productionSource')!=SOURCE or original.get('productionSource')!=SOURCE or r['classByteMismatch']!=0 or r['qualified2770Tests']!=3673 or r['all1643MainMembersIdentical']!=1643 or r['oldNativeImported']is not False or full['result']['tests']!=3673:
        raise ValueError('qualified current Main/all member/current session authority required')
    files={str(i)+'.exec':v['sha256']for i,v in enumerate(original['selected'])if not(v['unit']=='schubert-nk-inbox-inspector.service'and v['relative'].endswith('.terminal.exec'))}
    if len(files)!=9:raise ValueError('exact latest-closing nine streams required')
    return {'manifestSha256':receipt['manifestSha256'],'files':files}


def server():
    raw=previous.server().replace('PG2750','PG2780').replace('Pg2750BackupHandoffLauncher','Pg2780ResumeSkippedLauncher').replace(
        'source-full-PG2744','source-full-PG2770').replace('PG2746-native-v2','PG2774-native-v1')
    compile(raw,'<actual isolated PG resume history>','exec');return raw


def transport_body():
    raw=inspect.getsource(previous.transport.main).replace('PG2220','PG2780').replace('pg2220','pg2780').replace(
        'pg2125-metadata-boundary-full-qualified-v1','pg2772-db-contract-full-qualified-v1')
    raw=raw.replace(",'libraries':libs}",",'libraries':libs,'native':native_input()}")
    if raw.count('PG2780-selected-v1')!=5:raise ValueError('complete one new-only transport role required')
    compile(raw,'<resume skip completed transport>','exec');return raw


def main():
    ns={**previous.transport.__dict__,'SOURCE':SOURCE,'FILES':FILES,'SLOT':'pg2780-resume-skip-history-selected-v1','SERVER':server(),'native_input':native_input}
    exec(compile(transport_body(),'<actual resume skip fixed source>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
