"""Fresh902 post v2: genuine captured20/source first, strict GC current second; no restart."""
import ast,json
from pathlib import Path
import pg901_bootstrap_post as prior
R=Path(__file__).resolve().parent
def payload(proof,seals):
 raw=prior.payload(proof,seals)
 hashes=json.loads((prior.W/'pg894-frozen-v3.safe.json').read_bytes())['fileHashes']
 authenticate='''
tools=base/'pg894-bootstrap-tools-v3'
require({p.name for p in tools.iterdir()}==set(BOOT_HASHES)|{'payload-sha256.json'})
for name,digest in BOOT_HASHES.items():
 p=tools/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and hashlib.sha256(p.read_bytes()).hexdigest()==digest)
require(json.loads((tools/'payload-sha256.json').read_bytes())==BOOT_HASHES)
current_bootstrap=show(bootstrap,STATE_FIELDS)
require(current_normal_or_gc(terminal,current_bootstrap))
current_configuration=complete_configuration(command(['systemctl','show',bootstrap,'--property='+','.join(sorted(FIELDS))]).decode(),bootstrap)
require(CONFIG['same'](boot_after['configuration'][bootstrap],current_configuration,exec_record))
after={**after,'units':{**after['units'],bootstrap:current_bootstrap},'configuration':{**after['configuration'],bootstrap:current_configuration}}
'''
 marker='bus=dbus.SystemBus(private=True);';assert raw.count(marker)==1
 raw=raw.replace(marker,(R/'pg902_terminal_current.py').read_text()+'\n'+authenticate+'\n'+marker)
 raw=raw.replace('pg901-bootstrap-post-v1','pg901-bootstrap-post-v2').replace('PG901-bootstrap-post-v1','PG901-bootstrap-post-v2')
 marker="result['currentCredentialsRetired']=True";assert raw.count(marker)==1
 raw=raw.replace(marker,marker+"\nresult['capturedNormal20VerifiedBeforeCurrent']=True\nresult['currentGcHistoryEmpty']=current_bootstrap!=terminal\nresult['gcDoesNotInferPastSuccess']=True")
 ast.parse(raw);return 'BOOT_HASHES='+repr(hashes)+'\n'+raw
if __name__=='__main__':
 source=(R/'pg901_bootstrap_post.py').read_text();env={'__file__':str(R/'pg901_bootstrap_post_v2.py'),'__name__':'post_v2'}
 exec(compile(source,'<901 shared readonly dispatcher>','exec'),env)
 env['payload']=payload
 # The dispatcher's output slot also must be fresh.
 main_source=source[source.index('def main():'):source.index("if __name__=='__main__':")].replace('pg901-bootstrap-post-v1','pg901-bootstrap-post-v2')
 exec(compile(main_source,'<901 separate post v2>','exec'),env);env['main']()
