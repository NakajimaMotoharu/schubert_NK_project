"""Read-only actual fresh Backup canonical/files/config/dump-list/DB oracle."""
import inspect
import pg1257_fresh_independent_terminal_post as transport
import pg1259_fresh_backup_manifest_oracle as oracle

SEALS={'before.private.json':'8679f1fc50bfe6a1f13d196f314e2c40463050b598decfd0468c382f9e34dd84','after.private.json':'7b48c21af7d30d0bdad3d0341ad3a29412fff405540ef95c0ca97328608f8f77','complete.private':'8f31ba931b056ae9776855ac503403e9688eb34316873169eb20205aae3badae','parent.private.jsonl':'ad8e71d357809fce1db1aa9f1e8c6a6e6a954b6bf8ccdf5672f2044957f6c28f'}

def payload(seals):
    if seals!=SEALS:raise ValueError('fixed actual fresh post seals required')
    s=transport.payload(seals);s=s[:s.index("save=base/'pg1257-fresh-terminal-post-v1'")]
    s+='\nORACLE_SOURCE='+repr(inspect.getsource(oracle))+'\n'+BODY
    compile(s,'<actual independent fresh Backup capture>','exec');return s

BODY=r'''
import types,pwd,io,tarfile
oracle=types.ModuleType('independent_ss_backup');exec(ORACLE_SOURCE,oracle.__dict__)
backup_identity=pwd.getpwnam('schubert-backup')
directory=pathlib.Path('/srv/schubert-nk/backup/20261011-050327-9f651096-aef9-4fba-90b0-a653e99f035a')
md=directory.lstat();require(stat.S_ISDIR(md.st_mode)and(md.st_uid,md.st_gid,stat.S_IMODE(md.st_mode))==(backup_identity.pw_uid,backup_identity.pw_gid,0o700)and md.st_nlink>=2 and not os.listxattr(directory))
require({p.name for p in directory.iterdir()}=={'MANIFEST.json','schubert_nk.dump','config.tar','credentials.tar.age'})
held=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
def fixed_read(name,maximum,owner):
 fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=held)
 try:
  st=os.fstat(fd);require(stat.S_ISREG(st.st_mode)and(st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode),st.st_nlink)==(*owner,0o600,1)and st.st_dev==md.st_dev and 0<st.st_size<=maximum and not os.listxattr(fd))
  body=os.pread(fd,st.st_size+1,0);require(len(body)==st.st_size and os.pread(fd,1,st.st_size)==b'')
  require(metadata9(os.fstat(fd))==metadata9(st)and metadata9(os.stat(name,dir_fd=held,follow_symlinks=False))==metadata9(st))
  return body,{'size':len(body),'sha256':hashlib.sha256(body).hexdigest()}
 finally:os.close(fd)
def observe_backup():
 manifest,manifest_digest=fixed_read('MANIFEST.json',4096,(0,0));physical={};buffers={}
 for name in oracle.FILES:
  owner=(backup_identity.pw_uid,backup_identity.pw_gid)if name=='schubert_nk.dump'else(0,0)
  body,digest=fixed_read(name,33554432,owner);physical[name]=digest
  if name=='schubert_nk.dump':require(body.startswith(b'PGDMP'))
  elif name=='credentials.tar.age':require(body.startswith(b'age-encryption.org/v1\n'))
  else:buffers[name]=body
 signed_hashes={a['path']:a['sha256']for a in data['artifacts']}
 profile_raw=pathlib.Path('/etc/schubert-nk/backup-profile.json').read_bytes();require(hashlib.sha256(profile_raw).hexdigest()==signed_hashes['config/effective/backup-profile.json']);profile=json.loads(profile_raw)
 recipient=pathlib.Path('/etc/schubert-nk/backup-age-recipient').read_bytes();require(re.fullmatch(b'age1[023456789acdefghjklmnpqrstuvwxyz]{58}\n',recipient)is not None and hashlib.sha256(recipient).hexdigest()==signed_hashes['config/effective/backup-age-recipient'])
 recipient_sha=hashlib.sha256(recipient).hexdigest()
 summary=oracle.verify(manifest,physical,profile,after['rows']['schubert.batch_runs'],'9f651096-aef9-4fba-90b0-a653e99f035a','2026-10-10T20:03:22.718197Z',recipient_sha)
 require(summary['directoryName']==directory.name)
 names={'common.yml','api.yml','web.yml','batch.yml','api.env','web.env','backup-profile.json','inbox-inspector.env'}
 with tarfile.open(fileobj=io.BytesIO(buffers['config.tar']),mode='r:')as tar:
  members=tar.getmembers();require(len(members)==8 and{m.name for m in members}==names and all(m.isreg()and not m.islnk()and not m.issym()and m.size<=1048576 for m in members))
  for m in members:
   source=pathlib.Path('/etc/schubert-nk')/m.name;st=source.lstat();require(stat.S_ISREG(st.st_mode)and(st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode))==(m.uid,m.gid,m.mode))
   with tar.extractfile(m)as content:body=content.read(1048577)
   require(len(body)==m.size and body==source.read_bytes()and hashlib.sha256(body).hexdigest()==signed_hashes['config/effective/'+m.name]and metadata9(source.lstat())==metadata9(st))
 return summary,{'manifestSha256':manifest_digest['sha256'],'archiveHashes':physical,'publicRecipientFingerprintVerified':True,'staticConfigAllowlistEntriesVerified':8}
try:
 first=observe_backup();require(first==observe_backup()and metadata9(directory.lstat())==metadata9(md)and metadata9(os.fstat(held))==metadata9(md))
 listing=subprocess.run(['sudo','-n','-u','schubert-backup','/usr/bin/pg_restore','--list',str(directory/'schubert_nk.dump')],capture_output=True,timeout=30)
 require(listing.returncode==0 and not listing.stderr and 0<len(listing.stdout)<=1048576)
 require(first==observe_backup())
finally:os.close(held)
save=base/'pg1260-fresh-backup-independent-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
with(save/'dump-list.private').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(listing.stdout);f.flush();os.fsync(f.fileno())
result={'run':'PG1260-fresh-backup-independent-v1','actualExit':0,'productionSource':'d5b00104280028d9ea81b44c1d1c805f3c2861ed','independentBackupSummary':first[0],'independentPhysicalSummary':first[1],'ordinaryBackupPgRestoreListExit':0,'dumpListSha256':hashlib.sha256(listing.stdout).hexdigest(),'all24Full32Signed187OriginalStartupPreserved':True,'allTenKernelActorsClientsAdvisoryFlocks0':True,'startsStopsReloadsSqlWrites0':True,'restoreAndGenerationPruneAccepted':False,'plaintextExported':False,'formalAccepted':False}
with(save/'result.safe.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
for p in [save,save.parent]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps(result))
'''

def main():
    entry=inspect.getsource(transport.main).replace('pg1257-fresh-terminal-post-v1','pg1260-fresh-backup-independent-v1')
    env=dict(transport.__dict__);env['payload']=payload
    exec(compile(entry,'<new-only independent Backup actual capture>', 'exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
