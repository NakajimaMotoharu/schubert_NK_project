"""SSC249/250/264 newboot empty-startup finite publication with retained original inode."""
import ast
import inspect
import json
import types
from pyflakes.api import check
import pg2842_network_cold_ro_sources as ro
import pg1083_cold_publication_contract as finite
import pg1088_cold_exchange_io as exchange
import pg1090_cold_finite_capture as capture
from pg1091_cold_activation_sources import PUBLISH
from pg1091_cold_activation_refs import BODY

CLASS='Pg2852NetworkColdPublication'
TOOLS='pg2852-network-cold-publication-tools-v1'
SAVE='pg2858-network-cold-publication-completed-v1'
REF='pg2852_network_cold_publication_refs.py'
RO_AFTER='b9a4eb1dcf71e4e514f689734ca54bf1471c19b4aa4f2e7b8d27b471c3ae06ee'
unused=ro.unused


def bind(raw):
    raw=ro.bind(raw)
    for a,b in [(ro.CLASS,CLASS),(ro.TOOLS,TOOLS),(ro.SAVE,SAVE),(ro.REF,REF),('PG2848_', 'PG2858_'),
        ('Pg1091ColdActivation',CLASS),('pg1091-cold-activate-v1',SAVE),('pg1091-approval.part','pg2852-approval.part'),
        ('PG1091_', 'PG2858_'),('pg1088-current.part','pg2852-current.part'),
        ('cbca8738-3b24-4090-b77c-bf029677cdd6',ro.unused.current.BOOT),
        ('eeae04ea-713c-4f2d-888d-358fb4bed274','77601cf8-0ade-40fd-813f-c81d5210845e'),
        ('091663ce-1cf4-47e7-8311-218ebb0c8653','26250063-8755-43b6-9ac7-f76d5eee7257'),
        ('2026-10-09T23:31:22.087768Z','2026-10-14T06:56:07.778154Z'),
        ('b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524',ro.unused.current.BOM)]:raw=raw.replace(a,b)
    return raw


def protocol():
    m=types.ModuleType('newboot_finite_publication');exec(bind(inspect.getsource(finite)),m.__dict__);return m


def qualify():
    v=json.loads((ro.unused.current.W/'pg2850-network-cold-ro-independent-post-v1/manifest.safe.json').read_bytes());g=v.get('guest',{})
    if v.get('actualExit')!=0 or g.get('candidateSource')!=ro.unused.CANDIDATE or g.get('boot')!=ro.unused.current.BOOT or g.get('candidateImmutableIndependentPost')is not True or g.get('parentBackendAdvisoryFlocksGone')is not True or g.get('prepareAfterSha256')!=RO_AFTER:
        raise ValueError('genuine independent cold candidateRO proof required')


def java():
    raw=bind(ro.java());raw=ro.unused.one(raw,'"prepare-ro".equals(args[0])','"activate".equals(args[0])')
    raw=ro.unused.one(raw,'Set.of("prepare","prepared","run")','Set.of("prepare","epoch","approval","exchange","run")')
    raw=ro.unused.one(raw,'"verify",Integer.toString(backend)','Integer.toString(backend)')
    start=raw.index('              phase="NECESSARY_CANDIDATE_HOST_RO";');end=raw.index('              phase="FULL_IMMUTABLE_CANDIDATE";',start)
    raw=raw[:start]+'''              phase="ALREADY_QUALIFIED_CANDIDATE_RO";
              require(readOnlyMount(Files.readString(Path.of("/proc/self/mountinfo")),Pg387TrustedDeployment.RELEASE.toString()));
'''+raw[end:]
    marker='              Pg387TrustedDeployment.LABEL="PG2654";Pg387TrustedDeployment.STEM="pg2654";'
    raw=ro.unused.one(raw,marker,'              phase="FINITE_COLD_PUBLICATION";publication(candidate,refs,session);\n'+marker)
    raw=ro.unused.one(raw,'              refs.check("prepared");original(session);','              original(session);')
    raw=ro.unused.one(raw,'  public static void main(String[] args)throws Exception {',bind(PUBLISH)+'\n  public static void main(String[] args)throws Exception {')
    return raw.replace('candidateImmutableVerified=true','finiteColdActivation=true')


def runtime_function():
    return '''def runtime_namespaces():
 root=pathlib.Path('/run/schubert-nk')
 require(set(os.listdir(root))=={'maintenance.lock','startup-admission.lock','maintenance','startup','backup-request','cleanup-request','expiry-request','pt-coverage'})
 value={name:metadata(root/name)for name in expected_runtime if name not in {'@root','children'}}
 value['@root']=metadata(root)
 value['children']={name:metadata(root/'pt-coverage'/name)for name in expected_runtime['children']}
 require(set(value)==set(expected_runtime)and value['children']==expected_runtime['children'])
 for name,m in value.items():
  if name=='children':continue
  p=root if name=='@root'else root/name;require(not os.listxattr(p))
  if name=='startup':
   require(m==tree_records()[pub.STARTUP][pub.STARTUP]['metadata'])
   require(set(os.listdir(p))==({'epoch.current'}if PHASE!='before'else set()))
   if PHASE!='before':require((p/'epoch.current').read_bytes()==EPOCH)
  else:require(m==expected_runtime[name])
  if name not in ('@root','pt-coverage','startup','maintenance.lock','startup-admission.lock'):require(not os.listdir(p))
 require(set(os.listdir(root/'pt-coverage'))==set(expected_runtime['children']))
 for name in expected_runtime['children']:
  p=root/'pt-coverage'/name;require(not os.listdir(p)and not os.listxattr(p))
 return value
runtime_check=runtime_namespaces
'''


def observer():
    qualified=ro.observer();prefix=qualified.split('import dbus,time,sys,types\n',1)[0]
    prefix=ro.unused.one(prefix,'require(pathlib.Path(\'/opt/schubert-nk/current\').readlink()==release)',
        "require(str(pathlib.Path('/opt/schubert-nk/current').readlink())==(pub.NEW_LINK if PHASE in ('after','release')else pub.OLD_LINK))")
    tree=ast.parse(qualified);helpers=[]
    for n in tree.body:
        if isinstance(n,ast.FunctionDef)and n.name in {'peer_check','hold_material','authenticate_candidate','authenticate'}:
            helpers.append(ast.get_source_segment(qualified,n))
    if len(helpers)!=4:raise ValueError('complete fresh real backend and held authentication functions required')
    body=bind(BODY)
    # The original rows/Units are immutable data, not old runtime/owner authority.
    start=body.index("old=json.loads(pathlib.Path(");end=body.index('prepared=json.loads(prepared_raw);',start)
    body=body[:start]+"prepared_raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg2848-network-cold-ro-completed-v1/after.private.json').read_bytes()\nrequire(hashlib.sha256(prepared_raw).hexdigest()=="+repr(RO_AFTER)+")\n"+body[end:]
    body=body.replace('CONTRACT_SOURCE','INVENTORY_SOURCE').replace('import types,dbus,sys,time,traceback','import types,dbus,sys,time')
    body=body.replace("prepared['snapshot']","prepared['current']")
    body=body.replace("OWNER_BACKEND=0;after=pair()","OWNER_BACKEND=0;PEER_CLOSED=True;after=pair()")
    body=ro.unused.one(body,"PHASE='link-staged';pair()","PHASE='link-staged';private('link-staged.private.json',pair())")
    body=ro.unused.one(body,"phase='NORMAL_RELEASE';require(sys.stdin.readline()=='release\\n');inventory_check(tree_records())",
        "phase='NORMAL_RELEASE';require(sys.stdin.readline()=='release\\n');PHASE='release';private('release.private.json',pair());inventory_check(tree_records())")
    tree=ast.parse(body);runtime=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='runtime_namespaces')
    body=ro.unused.one(body,ast.get_source_segment(body,runtime),runtime_function())
    old="require(a==b and a['units']==prepared['current']['units']and a['rows']==prepared['current']['rows']and a['durable']==prepared['current']['durable']and a['artifacts']==prepared['current']['artifacts'])"
    body=ro.unused.one(body,old,"require(a==b and a==prepared['current'])")
    body=ro.unused.one(body," for name,value in a['configuration'].items():require(same(prepared['current']['configuration'][name],value,exec_record))\n",'')
    body=ro.unused.one(body,"return {'immutable':a,'trees':trees,'runtime':runtime_namespaces()}",
        "return {'immutable':a,'trees':trees,'runtime':runtime_namespaces(),'parent':captured_parent,'beginNs':BEGIN_NS}")
    # Source042 authenticate() checks full retained approval; publication oracle
    # separately governs the one allowed atomic replacement after the before phase.
    helpers='\n\n'.join(helpers)
    helpers=bind(helpers)
    controls="""def controls():
 peer_check()
 require(pathlib.Path('/proc/self/ns/mnt').readlink()==pathlib.Path('/proc/1/ns/mnt').readlink())
 for target in (pub.OLD_LINK,pub.NEW_LINK):
  flags=command(['findmnt','--target',target,'--noheadings','--output','VFS-OPTIONS'],4096).decode().strip().split(',')
  require('ro'in flags and 'rw'not in flags)
"""
    authstart=body.index("try:\n phase='AUTHENTICATE'")
    body=body[:authstart]+"PID=OWNER_PID;BACKEND=OWNER_BACKEND;PEER_CLOSED=False\nrelease=pathlib.Path(pub.OLD_LINK)\n"+helpers+'\n'+controls+body[authstart:]
    head='PUB_SOURCE='+repr(bind(inspect.getsource(finite)))+'\nIO_SOURCE='+repr(inspect.getsource(capture))+'\nEXCHANGE_SOURCE='+repr(bind(inspect.getsource(exchange)))+'\n'
    code=head+prefix+body
    if check(code,'<whole finite cold publication graph>'):raise ValueError('complete finite publication namespace required')
    compile(code,'<newboot cold finite mutation and retained inode>','exec');return code


def java_test():return bind(ro.java_test()).replace('"prepare-ro"','"activate"')


if __name__=='__main__':raise SystemExit('factory only, no publication authority')
