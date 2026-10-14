"""SSC249: finite host RO on authenticated unuseda9, full verifier, no publication."""
import ast
import json
from pyflakes.api import check
import pg2832_network_cold_unused_sources as unused
from pg1084_cold_candidate_ro_sources import files as historical,CANDIDATE_AUTH
from pg835_pending_v5 import METHOD,ORACLE

CLASS='Pg2842NetworkColdCandidateRo'
TOOLS='pg2842-network-cold-ro-tools-v1'
SAVE='pg2848-network-cold-ro-completed-v1'
REF='pg2842_network_cold_ro_refs.py'


def bind(raw):
    for a,b in [(unused.CLASS,CLASS),(unused.TOOLS,TOOLS),(unused.SAVE,SAVE),(unused.REF,REF),('PG2838_','PG2848_'),
        ('PG1068','PG2802'),('pg1068','pg2802'),('PG932','PG2654'),('pg932','pg2654'),
        ('d5b00104280028d9ea81b44c1d1c805f3c2861ed',unused.CANDIDATE),
        ('40ef6e894573d2ffab1d1732124960f9c98d5f97',unused.current.SOURCE),
        ('0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d',unused.DIGEST),
        ('5715949985848b49b4acf23aeb2e30ea1ecfca925e94e36baa735b1e4d18152b',unused.SIGNATURE)]:raw=raw.replace(a,b)
    return raw


def qualify():
    v=json.loads((unused.current.W/'pg2840-network-cold-unused-independent-post-v1/manifest.safe.json').read_bytes())
    g=v.get('guest',{})
    if v.get('actualExit')!=0 or g.get('actualExit')!=0 or g.get('candidateSource')!=unused.CANDIDATE or g.get('boot')!=unused.current.BOOT or g.get('candidateFull187Verified')is not True or g.get('candidateNotActivated')is not True:
        raise ValueError('full independent unused candidate/newboot proof required')


def java():
    raw=bind(unused.java());raw=unused.one(raw,'"place".equals(args[0])','"prepare-ro".equals(args[0])')
    prior=historical()['Pg1084ColdCandidateRo.java']
    start=prior.index('              phase="CANDIDATE_HOST_NAMESPACE";')
    end=prior.index('              refs.check("prepared");original(session);',start)
    candidate=bind(prior[start:end])
    raw=unused.one(raw,'              phase="SIGNED_UNUSED_CANDIDATE_PLACEMENT";\n',candidate)
    method=METHOD.replace('PG832','PG2802').replace('\\\\n','\\n')
    raw=unused.one(raw,'  public static void main(String[] args)throws Exception {',method+'\n  public static void main(String[] args)throws Exception {')
    return raw.replace('unusedCandidatePlacement=true','candidateImmutableVerified=true')


def observer():
    raw=bind(unused.observer('1'*64))
    raw=unused.one(raw,"[b'"+CLASS+"',b'place',b'']","[b'"+CLASS+"',b'prepare-ro',b'']")
    tree=ast.parse(raw);root=next(n for n in tree.body if isinstance(n,ast.Try))
    loop=next(n for n in root.body if isinstance(n,ast.For)and ast.unparse(n.iter)=='sys.stdin')
    action=next(n for n in loop.body if isinstance(n,ast.If)and isinstance(n.test,ast.Compare)and ast.unparse(n.test)=="action == 'prepared'")
    old=ast.get_source_segment(raw,action)
    auth=bind(CANDIDATE_AUTH[:CANDIDATE_AUTH.index(' candidate_options=')])
    # Qualified held-file contract supplies fixed content, metadata, root0400 and normal close.
    material="""def hold_material(path,size,digest):
 h=contract.HeldInventory(str(path.parent),[{'path':path.name,'size':size,'sha256':digest}],0).open_file()
 require(h.capture()[-1][1][2:6]==(0,0,stat.S_IFREG|0o400,1));held.append(h)
def authenticate_candidate():
"""+auth+'\n'
    raw=unused.one(raw,'def authenticate():',material+'def authenticate():')
    raw=unused.one(raw,old,"if action=='prepared':\n   opts=command(['findmnt','--target',str(candidate_root),'--noheadings','--output','VFS-OPTIONS'],4096).decode().strip().split(',')\n   require('ro'in opts and 'rw'not in opts)")
    # candidate_root is a fixed module identity, not a local mutable current alias.
    raw=unused.one(raw,'def authenticate_candidate():',"candidate_root=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG2802')\ndef authenticate_candidate():")
    raw=unused.one(raw,' fixed_parent=actor();before_inventory=[]',
        ' authenticate();authenticate_candidate();fixed_parent=actor();before_inventory=[h.capture()for h in held]')
    # No archive input or stage action remains in the RO graph.
    raw=unused.one(raw,"BUNDLE_HASH='"+'1'*64+"'\n",'')
    if check(raw,'<whole authenticated cold RO graph>'):raise ValueError('complete RO namespace required')
    compile(raw,'<owned candidate immutable graph>','exec');return raw


def java_test():
    raw=bind(unused.java_test()).replace('"place"','"prepare-ro"')
    oracle=ORACLE.replace('PG832','PG2802').replace('Pg835PendingDeployment',CLASS).replace('\\\\n','\\n')
    return unused.one(raw,'    System.out.println(',oracle+'\n    System.out.println(')


if __name__=='__main__':raise SystemExit('factory only, no RO action')
