"""SSC247: unused signed candidate placement under completed-cold ownership.

No epoch/current/approval/Unit/DB writes. Existing current is host RO throughout.
The sibling placement changes releases parent metadata; held-current ancestry is
acquired AFTER this explicitly delimited mutation, never rebased or ignored.
"""
import ast
from pathlib import Path
from pg1062_cold_preparation_sources_v2 import files as previous
from pg936_stage_candidate import payload as old_stage

HERE=Path(__file__).resolve().parent
DIGEST='0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d'
SOURCE='d5b00104280028d9ea81b44c1d1c805f3c2861ed'


def replace_once(text,old,new):
    if any(type(x)is not str for x in (text,old,new))or not old or text.count(old)!=1:
        raise ValueError('fixed cold stage source refused')
    return text.replace(old,new)


def stage_body():
    raw=old_stage()
    raw=raw[raw.index(" root=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG932')"):]
    raw=raw[:raw.index(' terminal();assert current.readlink()==old;assert protected()==before')]
    raw='\n'.join(line[1:]for line in raw.splitlines())+'\n'
    raw=raw.replace('PG932','PG1068').replace('pg932','pg1068').replace('pg936-stage-v6','pg1071-candidate-input-v1').replace('pg936-release-v6.tar','pg1071-release-v1.tar')
    # Host-fixed hashes and archive policy are embedded into the frozen child.
    prefix="import grp,tarfile\nSOURCE="+repr(SOURCE)+"\nDIGEST="+repr(DIGEST)+"\n"
    prefix+='CONTRACT='+repr((HERE/'pg601_stage_contract.py').read_text())+'\n'
    prefix+="bundle=pathlib.Path('/home/ubuntu/pg1071-candidate-input-v1/bundle.safe.json')\n"
    prefix+="bundle_raw=bundle.read_bytes();require(hashlib.sha256(bundle_raw).hexdigest()==BUNDLE_HASH)\n"
    prefix+="bundle_data=json.loads(bundle_raw);require(set(bundle_data)=={'archiveSha256','signatureSha256'})\n"
    prefix+="TARHASH=bundle_data['archiveSha256'];SIGHASH=bundle_data['signatureSha256']\n"
    ast.parse(prefix+raw)
    # No candidate assignment may escape into the existing-current observer.
    return 'def place_candidate():\n'+''.join(' '+line+'\n'for line in (prefix+raw).splitlines())+'place_candidate()\n'


def files():
    result={}
    for name,text in previous().items():
        for old,new in [('Pg1062ColdOwnedPreparation','Pg1069ColdCandidateStage'),
                        ('pg1062_cold_refs.py','pg1069_cold_refs.py'),
                        ('pg1062-cold-tools-v1','pg1069-cold-tools-v1'),
                        ('pg1062-cold-prepared-v1','pg1069-cold-candidate-v1'),
                        ('PG1062_','PG1069_')]:
            name=name.replace(old,new);text=text.replace(old,new)
        if name.endswith('.java')and not name.endswith('Test.java'):
            start=text.index('  static void environment()throws Exception {')
            end=text.index('\n  public static void main',start)
            text=text[:start]+text[end:]
            text=replace_once(text,'"prepare".equals(args[0])','"place".equals(args[0])')
            text=replace_once(text,'if(!readonlyOptions(new String(mount,StandardCharsets.US_ASCII).strip()))Pg387TrustedDeployment.freezeCandidate();',
                              'require(readonlyOptions(new String(mount,StandardCharsets.US_ASCII).strip()));')
            text=replace_once(text,'phase="FINITE_EMPTY_NAMESPACES";environment();','phase="SIGNED_UNUSED_CANDIDATE_PLACEMENT";')
            text=text.replace('finitePreparation=true','unusedCandidatePlacement=true')
        elif name.endswith('Test.java'):
            # Existing literal argument oracle now accepts place, rejects prepare.
            text=text.replace('"prepare"','"place"')
        else:
            text=replace_once(text,"b'Pg1069ColdCandidateStage',b'prepare',b''", "b'Pg1069ColdCandidateStage',b'place',b''")
            text=replace_once(text,'PREPARED=False','PREPARED=True')
            text=replace_once(text,"  if str(path)!='/run/schubert-nk'or not PREPARED:require(m==fixed)\n  else:require(m[5]==fixed[5]+5)","  require(m==fixed)")
            text=replace_once(text,"phase='BYTE_AUTH';captured_parent=parent();controls();authenticate()", "phase='BYTE_AUTH';captured_parent=parent();controls()")
            # Full RO verifier runs in the Java parent before this command.
            # Current namespace ancestry is pinned only after the sibling mutation.
            marker="phase='PREPARED';require(sys.stdin.readline()=='prepared\\n');PREPARED=True"
            action="phase='SIGNED_UNUSED_STAGE';require(sys.stdin.readline()=='prepared\\n')\n"
            action+=' '+stage_body().replace('\n','\n ').rstrip()+'\n authenticate()'
            text=replace_once(text,marker,action)
            ast.parse(text)
        result[name]=text
    return result
