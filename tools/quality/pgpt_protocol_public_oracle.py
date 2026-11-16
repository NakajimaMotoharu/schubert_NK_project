"""SS323/354: admit only the unchanged, source-reviewed Protocol public-type oracle.

This is not a general reflection capability. The original helper SHA and its four exact
lookups fix a closed semantic type set; no private access, arbitrary lookup or held type
is supported. Original successful130 is referenced as lineage, never reexecuted here.
"""
import json

HELPER='src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/layout/IndependentNamedFieldOracle.java'
HELPER_SHA='c7249b4a26e6515043c686362ce8b7d67e256c35bcb4cc01f8205bcaf7e3e06f'
PREFIX='src/schubert-nk-protocol/'
ANCHORS=['Class.forName(SEMANTIC + semantic)','Class.forName(SEMANTIC + "Sha256Hex")','Class.forName(SEMANTIC + "RelativePath")','Class.forName(SEMANTIC + "DisplayPath")']
SCALARS=['UserId','EntryId','AudioId','LogId','NotificationId','QuestionId','ScriptFileId','SpeakerId','AsyncJobId','GameCode','EntryType','VoiceCondition','ContentDisposition','DeliveryMode','PairRole','UserRole','LogLevel','LogType','UserState','NotificationState','AnswerState','NotificationType','NotificationErrorCode','MediaMimeType','HttpStatusCode','ElapsedMilliseconds','AnimationListCategory','VideoCategory','AnimationCategory','Sha256Hex','RelativePath','DisplayPath']

COLLECTION_BLOCK='\n    // PT-PRO-NAMED-RECORD-COLLECTION-BEGIN\n    Map<Object, String> recordIndex = new HashMap<>();\n    recordIndex.put(constructed, "typed-record");\n    assertEquals("typed-record", recordIndex.get(decoded));\n    org.junit.jupiter.api.Assertions.assertFalse(constructed.equals(null));\n    org.junit.jupiter.api.Assertions.assertFalse(constructed.equals("other-type"));\n    Map<Object, String> wireIndex = new HashMap<>();\n    wireIndex.put(new FieldValueSet(input), "wire-fields");\n    assertEquals("wire-fields", wireIndex.get(fieldsOf(decoded)));\n    // PT-PRO-NAMED-RECORD-COLLECTION-END'

def syntax(c):
 import pgpt_closed_host_profile as p
 v=c.get('reviewedProtocolPublicOracle')
 if v is None:return
 p.require(isinstance(v,dict) and set(v)=={'closureProof'} and v['closureProof'] in c['closureProofs'],'explicit independent public-oracle closure')
 p.require(len(c['mainSources'])==165,'reviewed complete Protocol Main closure only')
 module=(len(c['testSources']),c['expectedTests']) in [(31,140),(32,144),(33,145),(35,152)]
 record=len(c['testSources'])==2 and c['expectedTests']==6 and {x['path'] for x in c['testSources']}=={HELPER,PREFIX+'src/test/java/dev/codex/schubert/nk/protocol/layout/PayloadTypeCatalogTest.java'}
 legacy=len(c['testSources'])==3 and c['expectedTests']==19 and {x['path'] for x in c['testSources']}=={HELPER,PREFIX+'src/test/java/dev/codex/schubert/nk/protocol/layout/PayloadTypeCatalogTest.java',PREFIX+'src/test/java/dev/codex/schubert/nk/protocol/layout/WebLogActionContractTest.java'}
 p.require(module or record or legacy,'reviewed complete140 or exact record caller whole6/19 only')
 p.require(all(n.startswith(PREFIX) for n in c['mainSources']+[t['path'] for t in c['testSources']]),'Protocol-only source boundary')
 p.require(sum(t['path']==HELPER and t['tests']==0 for t in c['testSources'])==1,'unchanged whole helper required')
 p.require(c['sdkJars']==[],'no external SDK/backend capability')

def checked(c):
 import pgpt_closed_host_profile as p
 syntax(c)
 v=c.get('reviewedProtocolPublicOracle')
 if v is None:return
 pin=v['closureProof'];proof=json.loads((p.R/pin['path']).read_text());p.require(p.digest(p.R/pin['path'])==pin['sha256'] and proof['actualExit']==0,'public oracle proof hash')
 p.require(proof['helper']['path']==HELPER and proof['helper']['sha256']==p.digest(p.R/HELPER),'whole helper immutable against current closure')
 helper=(p.R/HELPER).read_text()
 if p.digest(p.R/HELPER)!=HELPER_SHA:
  import hashlib
  p.require(helper.count(COLLECTION_BLOCK)==1 and proof.get('additiveContractExtensionOriginalSha')==HELPER_SHA,'only exact additive collection contract block')
  p.require(hashlib.sha256(helper.replace(COLLECTION_BLOCK,'',1).encode()).hexdigest()==HELPER_SHA,'all original helper bytes/oracles exact under inverse')
 p.require(proof['lookupAnchors']==ANCHORS and proof['closedScalarTypes']==SCALARS and proof['privateOrHeldTypeAccess'] is False,'source-reviewed closed target set')
 for oldpin,tests in [(proof['historicalCompile'],None),(proof['historicalPost'],130)]:
  oldpath=p.R/oldpin['path'];old=json.loads(oldpath.read_text());p.require(p.digest(oldpath)==oldpin['sha256'] and old['actualExit']==0,'qualified historical proof identity')
  if tests is None:p.require(old['inputHashes'][HELPER]==HELPER_SHA,'historical helper byte pin')
  else:p.require(old['tests']==tests,'historical whole130 only')
 source=(p.R/HELPER).read_text();p.require(source.count('Class.forName')==4 and all(source.count(a)==1 for a in ANCHORS),'exact four public scalar lookups only')
 p.require('setAccessible' not in source and 'privateLookupIn' not in source,'no private access')
 for name in SCALARS:
  n='dev/codex/schubert/nk/protocol/layout/semantic/'+name
  p.relative_name(n);p.require(PREFIX+'src/main/java/'+n+'.java' in c['mainSources'] and n+'.class' in c['physicalClasses'],'every lookup target freshly compiled')
 p.require(len(proof['resourcePins'])==5,'five independent literal fixtures')
 for pin in proof['resourcePins']:
  p.require(pin['path'] in [x['path'] for x in c['resources']] and p.digest(p.R/pin['path'])==pin['sha256'],'same fixed independent resource')

def reviewed_text(c,path,text):
 if c.get('reviewedProtocolPublicOracle') is None or path!=HELPER:return text
 # Called only after checked(). Every removed token corresponds to one source-reviewed public lookup.
 for anchor in ANCHORS:text=text.replace(anchor,'REVIEWED_PUBLIC_SCALAR_LOOKUP',1)
 return text
