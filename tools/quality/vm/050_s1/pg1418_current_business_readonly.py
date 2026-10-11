"""Same current source/Root independent Backup and causal Log proof under all Ref.

No new business dispatch; preserves raw private evidence and separates completeness.
"""
import ast
import inspect
import json
import pg1400_existing_admin_independent_post as current
import pg1257_fresh_independent_terminal_post as transport
import pg1260_fresh_backup_independent_capture as backup
import pg1263_backup_config_responsibility_v2 as config
import pg1266_fresh_log_independent_capture as log
import pg1131_journal_stable_projection as journal
from pg1334_published_owned_stop_sources_v2 import SOURCE,W

RUN='d2e3a86f-27a4-4c2a-be21-b512eebf1216'
CUT='2026-10-10T23:30:23.481632Z'
BEFORE='3cb4a2cc52eed5e6fce68aa551c2af9ab65692ef0d5c5d7af9409a761cdecac9'
SLOT='pg1418-current-business-readonly-v1'

def backup_body():
    body=backup.BODY.split("save=base/'pg1260-fresh-backup-independent-v1'")[0]
    body=body.replace('20261011-050327-9f651096-aef9-4fba-90b0-a653e99f035a','20261011-083027-'+RUN)
    body=body.replace('9f651096-aef9-4fba-90b0-a653e99f035a',RUN).replace('2026-10-10T20:03:22.718197Z',CUT)
    old="require(len(body)==m.size and body==source.read_bytes()and hashlib.sha256(body).hexdigest()==signed_hashes['config/effective/'+m.name]and metadata9(source.lstat())==metadata9(st))"
    if body.count(old)!=1:raise ValueError('one explicit config authority boundary required')
    body=body.replace(old,"""require(len(body)==m.size and st.st_nlink==1 and not os.listxattr(source))
   expected_gid=pwd.getpwnam('schubert-api').pw_gid if m.name=='api.env'else pwd.getpwnam('schubert-web').pw_gid if m.name=='web.env'else grp.getgrnam('schubert').gr_gid
   config_oracle.verify_member(m.name,body,source.read_bytes(),(st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode)),(m.uid,m.gid,m.mode),expected_gid,signed_hashes)
   require(metadata9(source.lstat())==metadata9(st))""")
    marker="backup_identity=pwd.getpwnam('schubert-backup')"
    body=body.replace(marker,"import grp\nconfig_oracle=types.ModuleType('independent_config');exec(CONFIG_SOURCE,config_oracle.__dict__)\n"+marker)
    body+='\nbackup_result={**first[0],**first[1],"dumpListSha256":hashlib.sha256(listing.stdout).hexdigest(),"ordinaryBackupPgRestoreListExit":0}\n'
    return body

def log_body():
    body=log.BODY.split("save=base/'pg1266-fresh-independent-log-v1'")[0]
    body=body.replace('pg1238-fresh-day-ordinary-before-v1','pg1319-published-ordinary-before-v1').replace('57a5889403d752e2558f144b41e9ddd702451d78bf0deab5b6f2fd462b02966e',BEFORE)
    body=body.replace('4236e5a9bfd94fe09ca34323687bc5c3','588c880aed434af6a6bb89c7ad3bf076').replace('2026-10-10T20:03:22.718197Z',CUT)
    body=body.replace("old=json.loads(old_raw)['current'];require(old['source']==data['source']['commit'])","old=json.loads(old_raw)['current'];require(BEFORE_RECEIPT['actualExit']==0 and BEFORE_RECEIPT['productionSource']==data['source']['commit']==SOURCE and BEFORE_RECEIPT['privateBeforeSha256']==hashlib.sha256(old_raw).hexdigest()and BEFORE_RECEIPT['ordinaryNoargs']is True)")
    old="require(second.returncode==0 and not second.stderr and second.stdout==journal.stdout)"
    body=body.replace(old,"stable=types.ModuleType('independent_journal');exec(JOURNAL_SOURCE,stable.__dict__);require(second.returncode==0 and not second.stderr and 0<len(second.stdout)<=16777216 and stable.project(second.stdout)==stable.project(journal.stdout))")
    body=body.replace("run='PG1266-fresh-independent-log-v1'","run='PG1418-current-business-readonly-v1'")
    body+="\nlog_result=result\nrequire(after==value and native==snapshot()and native==snapshot())\n"
    # `value` has extra post metadata, whereas `after` is the core snapshot.
    body=body.replace('require(after==value and native==snapshot()and native==snapshot())','require(after["rows"]==value["rows"]and native==snapshot()and native==snapshot())')
    return body

def payload(seals):
    raw=current.payload(seals)
    tree=ast.parse(raw)
    scopes=[n for n in tree.body if isinstance(n,ast.Try)and any(isinstance(x,ast.For)and 'RefUnit' in ast.unparse(x)for x in n.body)]
    if len(scopes)!=1:raise ValueError('one exact all metadata Ref lifetime required')
    scopes[0].body.extend(ast.parse(backup_body()+'\n'+log_body()).body)
    for n in tree.body:
        if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='result'for t in n.targets):
            if not isinstance(n.value,ast.Dict):raise ValueError('one safe post dict required')
            n.value.keys.extend([ast.Constant('backup'),ast.Constant('causalLog')]);n.value.values.extend([ast.Name('backup_result',ast.Load()),ast.Name('log_result',ast.Load())])
    ast.fix_missing_locations(tree)
    raw=ast.unparse(tree).replace('pg1400-existing-admin-independent-post-v1',SLOT).replace('PG1400-existing-admin-independent-post-v1','PG1418-current-business-readonly-v1')
    receipt=json.loads((W/'pg1319-published-ordinary-before-v1.safe.json').read_bytes())
    receipt={k:receipt[k]for k in ('actualExit','productionSource','privateBeforeSha256','ordinaryNoargs')}
    definitions='SOURCE='+repr(SOURCE)+'\nBEFORE_RECEIPT='+repr(receipt)+'\nORACLE_SOURCE='+repr(inspect.getsource(backup.oracle))+'\nCONFIG_SOURCE='+repr(inspect.getsource(config))+'\nINDEPENDENT_SOURCE='+repr(log.independent_source())+'\nJOURNAL_SOURCE='+repr(inspect.getsource(journal))+'\n'
    compile(definitions+raw,'<fixed current business Ref/crypto/post graph>','exec');return definitions+raw

def main():
    if(W/'pg1396-execute-v3.exit').read_bytes()!=b'0\n':raise ValueError('current ADMIN completed required')
    env=dict(transport.__dict__,SOURCE=SOURCE,payload=payload)
    code=current.previous.previous.previous.previous.source().replace('pg1344-current-bootstrap-before-v1',SLOT)
    exec(compile(code,'<fresh readonly business transport>','exec'),env);return env['main']()

if __name__=='__main__':raise SystemExit(main())
