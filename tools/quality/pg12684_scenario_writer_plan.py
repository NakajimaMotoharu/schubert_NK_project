"""Finally-only cleanup and four typed writer fault modes; retain all independent original tokens."""
import difflib
import sys
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX

OUT=data.BASE/'PG12684-scenario-writer-plan-v1'
PATH='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/storage/ScenarioRecordStreamTest.java'
COMPANION='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/storage/TransferContentVerifierTest.java'
MODES={'ZERO_WRITE_MODE':1,'NEGATIVE_WRITE_MODE':2,'IO_FAILURE_MODE':3,'FORCE_FAILURE_MODE':4}
OLD_BLOCK='    closed.close();\n    reject(() -> prepared.write(closed));\n'
NEW_BLOCK='    try {\n      closed.close();\n      reject(() -> prepared.write(closed));\n    } finally {\n      closed.close();\n    }\n'

def raw(t):return [m.group() for m in LEX.finditer(t) if not m.group().startswith(('//','/*'))]

def eligibility():
 groups={
  'api/storage':['ScenarioRecordStream','TransferContentVerifier'],
  'protocol/codec':['PayloadCodec','FieldCodec','MessageEncodingException','FieldEncodingException','PermanentProtocolException'],
  'protocol/layout':['LayoutFieldCatalog','LayoutRegistry','LayoutDefinition','LayoutId','LayoutFields','FieldDefinition','FieldArea','WireType','Presence','Padding','FieldValueSet','FieldValue','TypedFieldValues','PayloadSemanticValidator','PayloadRecord','PayloadValues','FixedPayload','LayoutPayload','TypedPayloadValues','PayloadData','LayoutValidationException','UnsupportedLayoutException'],
  'protocol/layout/semantic':['EntryId','EntryType','AudioId','DisplayPath','IdValue','ProtocolId','PathSyntax','WireEnum','ElapsedMilliseconds','HttpStatusCode','RelativePath','Sha256Hex','AsyncJobId','LogId','NotificationId','QuestionId','ScriptFileId','SpeakerId','UserId'],
  'protocol/header':['MessageKind','InteractionKind','ResultCode','AuthenticationContext'],
  'protocol/time':['JstWireTimestamp'],
  'protocol/file':['LargeResultContent','LargeResultDescriptor'],
  'storage':['StorageIoException']}
 paths=[]
 for package,names in groups.items():
  role=package.split('/')[0]
  paths.extend('src/schubert-nk-'+role+'/src/main/java/dev/codex/schubert/nk/'+package+'/'+name+'.java' for name in names)
 return paths

def before():
 n=data.read_checked(data.BASE/'PG12666-transfer-verifier-six-compile-v1/manifest.json','138b454a9eb9d3d00f6ac2579d6f76b36afbc340b745375d53dfa8383bf59e10')
 root=Path(n['jars']['api']['path']).parent.parent.parent.parent;t=(root/PATH).read_text();assert data.sha(t.encode())==n['begin']['inputHashes'][PATH]
 return n,t

def declaration(name,value):return '    private static final int '+name+' = '+str(value)+';\n'

def intended(old):
 assert old.count(OLD_BLOCK)==1;t=old.replace(OLD_BLOCK,NEW_BLOCK)
 head='  private static final class FaultChannel extends FileChannel {\n';assert t.count(head)==1
 t=t.replace(head,head+''.join(declaration(k,v) for k,v in MODES.items())+'\n')
 for name,value in MODES.items():
  condition='if (mode == '+str(value)+')';assert t.count(condition)==1;t=t.replace(condition,'if (mode == '+name+')')
 return t

def require(old,new):
 t=new
 for name,value in MODES.items():
  decl=declaration(name,value);assert t.count(decl)==1;t=t.replace(decl,'')
  assert raw(t).count(name)==1 and t.count('if (mode == '+name+')')==1;t=t.replace('if (mode == '+name+')','if (mode == '+str(value)+')')
 assert t.count(NEW_BLOCK)==1;t=t.replace(NEW_BLOCK,OLD_BLOCK);assert raw(t)==raw(old)

def emit():
 _,old=before();new=intended(old);require(old,new);assert (data.ROOT/PATH).read_text()==old
 return '*** Begin Patch\n*** Update File: '+str(data.ROOT/PATH)+'\n'+'\n'.join('@@' if x.startswith('@@') else x for x in list(difflib.unified_diff(old.splitlines(),new.splitlines(),n=3))[2:])+'\n*** End Patch\n'

def main():
 invocation=capture(__file__);assert not OUT.exists();n,old=before();new=(data.ROOT/PATH).read_text();require(old,new)
 assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in n['begin']['inputHashes'].items() if p!=PATH)
 bads=[]
 for name,value in MODES.items():
  decl=declaration(name,value)
  bads.extend([new.replace(decl,'',1),new.replace(decl,declaration(name,value+1),1),new.replace(name,'WRONG_MODE',1)])
 bads.extend([new.replace('    } finally {\n      closed.close();\n    }','    } finally {\n    }',1),new.replace('@Test','@Disabled',1),new.replace('i < 16','i < 15',1),new.replace('put(expected, 164,','put(expected, 165,',1)])
 for bad in bads:
  assert bad!=new
  try:require(old,bad)
  except AssertionError:pass
  else:raise AssertionError('changed original fixture or non-owner finally accepted')
 eligible={p:n['begin']['inputHashes'][p] for p in eligibility()};assert len(eligible)==56
 assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in eligible.items())
 catalog=(data.ROOT/'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/LayoutFieldCatalog.java').read_text();blocks=[m for m in LEX.finditer(catalog) if m.group().startswith('"""')];assert len(blocks)==1
 spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2366_ScenarioWriter所有fixture五是正_単体テスト仕様書.md'
 verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=n['source'],invocation=invocation,sourceChanges=[dict(path=PATH,beforeSha256=data.sha(old.encode()),sha256=data.sha(new.encode()))],companionSourceHashes={COMPANION:n['begin']['inputHashes'][COMPANION]},eligibilityClosureSourceHashes=eligible,catalogDataOneTextblock=True,totalCorrections=5,typedConditionReferences=4,finallyOwnerOnlyChange=True,metadataNegativeVectors=len(bads),allMainAndOtherInputsUnchanged=True,originalWriterTests=5,requiredCompanionVerifierTests=3,originalTests=8,originalSuites=2,judgement='PT_DEFAULT_WHOLE_WRITER_VERIFIER_SELF_OWNED_NEW_TEMP_ONLY',heldNativeTestNotExtracted=True,specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),productTestsExecuted=0,newAccepted=0,coverage=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':
 if sys.argv[1:]==['--emit-patch']:print(emit(),end='')
 else:assert not sys.argv[1:];main()
