"""Read-only same-current full post guard and independent private Log/session oracle."""
import ast
import inspect
import pg1257_fresh_independent_terminal_post as transport
from pg1260_fresh_backup_independent_capture import SEALS
import pg564_log_session_oracle as core
import pg583_log_oracle as extension
import pg1243_fresh_day_rows_oracle as cleanup
import pg1265_fresh_log_cleanup_oracle as fresh


def independent_source():
    pieces = [inspect.getsource(core)]
    for module in (extension, cleanup, fresh):
        parsed = ast.parse(inspect.getsource(module))
        parsed.body = [n for n in parsed.body if not isinstance(n, ast.ImportFrom) or not n.module.startswith('pg')]
        pieces.append(ast.unparse(parsed))
    value = '\n'.join(pieces)
    compile(value, '<independent frozen fresh Log oracle>', 'exec')
    return value


def payload(seals):
    if seals != SEALS: raise ValueError('actual fixed current stop seals required')
    s = transport.payload(seals)
    s = s[:s.index("save=base/'pg1257-fresh-terminal-post-v1'")]
    s += '\nINDEPENDENT_SOURCE=' + repr(independent_source()) + '\n' + BODY
    compile(s, '<complete current guarded Log oracle>', 'exec')
    return s


BODY = r'''
import base64,types
oracle=types.ModuleType('independent_fresh_log');exec(INDEPENDENT_SOURCE,oracle.__dict__)
old_path=base/'pg1238-fresh-day-ordinary-before-v1/before.private.json'
old_stat=old_path.lstat();require(stat.S_ISREG(old_stat.st_mode)and(old_stat.st_uid,old_stat.st_gid,stat.S_IMODE(old_stat.st_mode),old_stat.st_nlink)==(0,0,0o600,1))
old_raw=old_path.read_bytes();require(metadata9(old_path.lstat())==metadata9(old_stat)and hashlib.sha256(old_raw).hexdigest()=='57a5889403d752e2558f144b41e9ddd702451d78bf0deab5b6f2fd462b02966e')
old=json.loads(old_raw)['current'];require(old['source']==data['source']['commit'])
journal_args=['journalctl','--boot=cbca87383b244090b77cbf029677cdd6','_SYSTEMD_INVOCATION_ID=4236e5a9bfd94fe09ca34323687bc5c3','-o','json','--no-pager']
journal=subprocess.run(journal_args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
require(journal.returncode==0 and not journal.stderr and 0<len(journal.stdout)<=16777216)
events=[]
for line in journal.stdout.splitlines():
 record=json.loads(line);message=record.get('MESSAGE','');require(type(message)is str)
 start=message.find('{')
 if start<0:continue
 try:event=json.loads(message[start:])
 except ValueError:continue
 if type(event)is dict and event.get('category')=='REQUEST':events.append(event)
require(len(events)==222)
keys=[];key_records=[]
try:
 for name in ('web-log-aes-current','web-session-aes-current'):
  p=pathlib.Path('/etc/schubert-nk/credentials')/name;fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
  try:
   st=os.fstat(fd);require(stat.S_ISREG(st.st_mode)and(st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode),st.st_nlink)==(0,0,0o600,1)and 0<st.st_size<=4096 and not os.listxattr(fd))
   raw=os.pread(fd,st.st_size+1,0);require(len(raw)==st.st_size and metadata9(os.fstat(fd))==metadata9(st)and metadata9(p.lstat())==metadata9(st))
   parts=raw.split(b'\n');require(len(parts)==4 and parts[0]==b'NKKEY1'and parts[1]==b'v1'and parts[3]==b'')
   key=bytearray(base64.b64decode(parts[2],validate=True));require(len(key)==32);keys.append(key);key_records.append((p,metadata9(st),hashlib.sha256(raw).digest()))
  finally:os.close(fd)
 result=oracle.verify_fresh(old['rows'],after['rows'],events,keys[0],keys[1],'2026-10-10T20:03:22.718197Z',222)
 require(all(e['appVersion']=='0.1.0-SNAPSHOT'for e in events))
 for p,meta,digest in key_records:
  require(metadata9(p.lstat())==meta and hashlib.sha256(p.read_bytes()).digest()==digest and metadata9(p.lstat())==meta)
finally:
 for key in keys:key[:]=b'\0'*len(key)
require(native==snapshot()and native==snapshot())
second=subprocess.run(journal_args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30);require(second.returncode==0 and not second.stderr and second.stdout==journal.stdout)
result.update(productionSource=data['source']['commit'],run='PG1266-fresh-independent-log-v1',sameCurrentSourceRun=True,all24Full32Signed187OriginalStartupPreserved=True,allTenKernelActorsClientsAdvisoryFlocks0=True,startsStopsReloadsSqlWrites0=True,keysExported=False,plaintextExported=False,requestJournalSha256=hashlib.sha256(journal.stdout).hexdigest(),formalAccepted=False)
save=base/'pg1266-fresh-independent-log-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
for name,raw in [('request-journal.private',journal.stdout),('result.safe.json',json.dumps(result,sort_keys=True).encode())]:
 with(save/name).open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(raw);f.flush();os.fsync(f.fileno())
for p in (save,save.parent):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps(result))
'''


def main():
    entry = inspect.getsource(transport.main).replace('pg1257-fresh-terminal-post-v1', 'pg1266-fresh-independent-log-v1')
    env = dict(transport.__dict__); env['payload'] = payload
    exec(compile(entry, '<new-only current Log transport>', 'exec'), env)
    return env['main']()


if __name__ == '__main__': raise SystemExit(main())
