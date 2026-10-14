"""SSC247/264: newboot signed unused candidate only; no ordinary/cold prepare replay."""
import ast
import json
from pyflakes.api import check
import pg2816_network_current_cold_sources as current
import pg2830_network_current_cold_post as post
from pg1069_cold_candidate_sources import stage_body as old_stage
from pg1079_cold_candidate_sources_v3 import files as old_files
from pg2814_network_newboot_readonly import one

CLASS='Pg2832NetworkColdUnusedCandidate'
TOOLS='pg2832-network-cold-unused-tools-v1'
SAVE='pg2838-network-cold-unused-completed-v1'
REF='pg2832_network_cold_unused_refs.py'
INPUT='pg2836-network-cold-unused-input-v1'
ARCHIVE='pg2834-network-cold-unused-release-v1.tar'
CANDIDATE='a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25'
DIGEST='37bfe01a075449d36cc8b73408dd81fc6d6efc158910a437cbde21b6a0b7f863'
SIGNATURE='93a6032cb7c3a15f010e521cea1da78ff6a975e2123462e70d808c59cfc10d11'
PREPARE_SHA='387f826c7603b7f2cdbaf39784a0996290ab0ae6b25832fe356dcbd24035bc9b'


def bind(raw):
    for a,b in [(current.CLASS,CLASS),(current.TOOLS,TOOLS),(current.PREPARED,SAVE),
        ('pg2816_network_current_cold_refs.py',REF),('PG2822_', 'PG2838_')]:raw=raw.replace(a,b)
    return raw


def qualify():
    v=json.loads((current.W/post.SLOT/'manifest.safe.json').read_bytes())
    g=v.get('guest',{})
    expected={'actualExit':0,'boot':current.BOOT,'source':current.SOURCE,'prepareAfterSha256':PREPARE_SHA,
        'fullCurrentDbOriginalBackupSignatureTwice':True,'parentBackendAdvisoryFlocksGone':True,
        'metadataScopesClosedNormally':True,'permissionIssued':False}
    if v.get('actualExit')!=0 or any(type(g.get(k))is not type(x)or g[k]!=x for k,x in expected.items()):
        raise ValueError('genuine current newboot independent finite post required')


def java():
    raw=bind(current.java())
    start=raw.index('  static void environment()throws Exception {');end=raw.index('\n  public static void main',start)
    raw=raw[:start]+raw[end:]
    raw=one(raw,'"prepare".equals(args[0])','"place".equals(args[0])')
    raw=one(raw,'if(!readonlyOptions(new String(mount,StandardCharsets.US_ASCII).strip()))Pg387TrustedDeployment.freezeCandidate();',
        'require(readonlyOptions(new String(mount,StandardCharsets.US_ASCII).strip()));')
    raw=one(raw,'phase="FINITE_EMPTY_NAMESPACES";environment();','phase="SIGNED_UNUSED_CANDIDATE_PLACEMENT";')
    return raw.replace('finitePreparation=true','unusedCandidatePlacement=true')


def stage_body():
    raw=old_stage()
    for a,b in [('d5b00104280028d9ea81b44c1d1c805f3c2861ed',CANDIDATE),
        ('0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d',DIGEST),
        ('PG1068','PG2802'),('pg1068','pg2802'),('pg1071-candidate-input-v1',INPUT),
        ('pg1071-release-v1.tar',ARCHIVE)]:raw=raw.replace(a,b)
    raw=one(raw,"TARHASH=bundle_data['archiveSha256'];SIGHASH=bundle_data['signatureSha256']",
        "TARHASH=bundle_data['archiveSha256'];SIGHASH=bundle_data['signatureSha256']\n require(SIGHASH=="+repr(SIGNATURE)+')')
    ast.parse(raw);return raw


def observer(bundle_hash):
    if type(bundle_hash)is not str or len(bundle_hash)!=64 or set(bundle_hash)-set('0123456789abcdef'):
        raise ValueError('exact frozen bundle SHA256 required')
    raw=bind(current.observer())
    raw=one(raw,"PID=os.getppid();phase='ENTRY';PREPARED=False;PEER_CLOSED=False",
        "PID=os.getppid();phase='ENTRY';PREPARED=True;PEER_CLOSED=False")
    raw=one(raw,"[b'"+CLASS+"',b'prepare',b'']","[b'"+CLASS+"',b'place',b'']")
    # Runtime metadata is the immutable actual finite-prepare oracle. No old tmpfs restored.
    tree=ast.parse(raw);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='runtime_check')
    old=ast.get_source_segment(raw,node)
    runtime=post.payload();rt=next(n for n in ast.parse(runtime).body if isinstance(n,ast.FunctionDef)and n.name=='runtime_check')
    new=ast.get_source_segment(runtime,rt)
    new=new[:new.index(" metas={n:runtime[n]")]+" global prepared_runtime\n prepared_runtime=runtime\n return runtime\n"
    raw=one(raw,old,new)
    marker="def actor():"
    oracle="""prepare_raw=(BASE/'pg2822-network-current-cold-prepared-v1/after.private.json').read_bytes()
require(hashlib.sha256(prepare_raw).hexdigest()==PREPARE_SHA)
before=json.loads(prepare_raw)
require(before['current']['boot']==BOOT and before['current']['source']==SOURCE)
"""
    raw=one(raw,marker,'PREPARE_SHA='+repr(PREPARE_SHA)+'\n'+oracle+marker)
    raw=one(raw,'value=[h.capture()for h in held];require(value==before_inventory)',
        'value=[h.capture()for h in held];require(value==before_inventory)')
    # Sibling placement intentionally changes releases parent metadata. Acquire held
    # current ancestry only AFTER this bounded mutation; never rebase an existing FD.
    start=raw.index(" phase='BEFORE_HELD_SIGNATURE'");end=raw.index(' bus=dbus.SystemBus(private=True)',start)
    block=raw[start:end]
    block=block[:block.index(' before_inventory=[h.capture()')]
    authenticate="release=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG2654')\n"+'def authenticate():\n global release,phase\n'+block+'\n'
    raw=raw[:start]+" fixed_parent=actor();before_inventory=[]\n"+raw[end:]
    raw=one(raw,'try:\n fixed_parent=actor();before_inventory=[]',authenticate+'try:\n fixed_parent=actor();before_inventory=[]')
    raw=one(raw,'first=snapshot();require(first==snapshot());inventory_check();framing',
        "first=snapshot();require(first==before['current'] and first==snapshot());inventory_check();framing")
    mutation="""  if action=='prepared':
   phase='SIGNED_UNUSED_STAGE'
"""+''.join('   '+line+'\n'for line in stage_body().splitlines())+"   authenticate();before_inventory=[h.capture()for h in held]\n"
    raw=one(raw,"  if action=='prepared':PREPARED=True\n",mutation)
    raw='BUNDLE_HASH='+repr(bundle_hash)+'\n'+raw
    if check(raw,'<newboot whole signed unused graph>'):raise ValueError('complete independent cold unused namespace required')
    compile(raw,'<owned cold unused graph>','exec');return raw


def java_test():
    raw=old_files()['Pg1079ColdCandidateStageTest.java']
    for a,b in [('Pg1079ColdCandidateStage',CLASS),('eeae04ea-713c-4f2d-888d-358fb4bed274','77601cf8-0ade-40fd-813f-c81d5210845e'),
        ('091663ce-1cf4-47e7-8311-218ebb0c8653','26250063-8755-43b6-9ac7-f76d5eee7257'),
        ('2026-10-09T23:31:22.087768Z','2026-10-14T06:56:07.778154Z'),('PT-DEP-1037001','PT-DEP-2832001')]:raw=raw.replace(a,b)
    return raw


if __name__=='__main__':raise SystemExit('factory only, no placement authority')
