"""Join current public design, independent fixtures, source owners and qualified execution metadata."""
from pathlib import Path
import datetime,hashlib,importlib,json,re,subprocess,sys
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sys.path[:0]=[str(b/'input'),str(r/'tools/quality')]
parser=importlib.import_module('4473_protocol_ui_trace_parser');import pgpt_closed_host_profile as policy
ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));core='7123bb3bc8319cfadea41e5be38a75e825e5c14c';cfgp=b/'input/4425_ssc447_profile.json';cfg=ld(cfgp);prep=ld(r/cfg['slots']['prepare']/'manifest.json');postp=b/'evidence/PG36623-ssc447-cache-owners-post-join-v1/manifest.json';old=ld(postp);rawp=b/'evidence/PG36624-ssc447-cache-owners-unfiltered-v1/manifest.json';raw=ld(rawp)
assert old['actualExit']==raw['actualExit']==0 and old['tests']==152 and old['physicalClasses']==175;now_inputs=policy.checked_inputs(cfg);assert now_inputs==prep['inputHashes']==old['inputHashes']
for path,h in now_inputs.items():assert sha(r/path)==h
for path in cfg['mainSources']:assert hashlib.sha256(subprocess.check_output(['git','show',core+':'+path])).hexdigest()==now_inputs[path]
for path,h in prep['dependencies'].items():assert sha(Path(path))==h
assert prep['toolHashes']==policy.tool_hashes();assert all(sha(postp.parent/name)==h for name,h in old['files'].items())
physical=prep['physicalClassHashes'];assert len(physical)==175 and physical==old['physicalClassHashes']==raw['classFileHashes'];folder=r.parent/'pgpt-runs/PG379'/cfg['privateDirs']['prepare']/'component'
for name in physical:policy.relative_name(name)
assert all(sha(folder/name)==h for name,h in physical.items());assert raw['oldExecCombined'] is False
mainByClass={p.split('/src/main/java/')[1][:-5]:p for p in cfg['mainSources']};assert len(mainByClass)==165;physicalSource={name:name[:-6].split('$')[0] for name in physical};assert set(physicalSource.values())==set(mainByClass)
inventoryp=r/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json';inv=ld(inventoryp);artifacts={a['path']:a for a in inv['artifacts']};req={x['id']:x for x in inv['requirements']};wbs=ld(r/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json');tasks={t['id']:t for t in wbs['tasks']};programs={t['program']:t for t in wbs['programs']};assert tasks['WBS-F01']['acceptance']['status']=='ACCEPTED';cases=prep['expectedCases'];assert len(cases)==152 and len({(x['classname'],x['name']) for x in cases})==152
mainTexts={p:(r/p).read_text() for p in cfg['mainSources']};testTexts={t['path']:(r/t['path']).read_text() for t in cfg['testSources']};casesByTest={p:[x['classname']+'#'+x['name'] for x in cases if x['classname'].split('.')[-1]==Path(p).stem] for p in testTexts}

def expand_ids(expression):
 out=[];prefix=None;letter='';width=3
 for chunk in re.split('[、/]',expression):
  chunk=chunk.strip()
  if re.fullmatch(r'[A-Z]+(?:-[A-Z]+)?',chunk):
   candidates=[key for key in req if key.startswith(chunk+'-' if '-' not in chunk else chunk)];assert candidates,chunk;out.extend(candidates);prefix=chunk.split('-')[0];letter=chunk.split('-')[1] if '-' in chunk else '';continue
  m=re.fullmatch(r'(?:(?P<prefix>[A-Z]+)-)?(?P<letter>[A-Z]?)(?P<start>\d+)(?:[～〜~](?:(?:[A-Z]+)-)?(?P<lastLetter>[A-Z]?)(?P<end>\d+))?',chunk.strip());assert m,expression
  prefix=m.group('prefix') or prefix;assert prefix;letter=m.group('letter') or ('' if m.group('prefix') else letter);width=len(m.group('start'));last=int(m.group('end') or m.group('start'));assert not m.group('lastLetter') or m.group('lastLetter')==letter
  for n in range(int(m.group('start')),last+1):
   key=prefix+'-'+letter+str(n).zfill(width);assert key in req,(expression,key);out.append(key)
 return sorted(set(out))

def doc(path):return subprocess.check_output(['git','show','origin/main:'+path],text=True)
docNames=['documents/200_UI/230_インターフェース/'+p.name for p in sorted((r/'documents/200_UI/230_インターフェース').glob('23[3456]*'))]+['documents/300_SS/320_メッセージング/323_全電文layout・Java・DB対応表.md','documents/300_SS/360_引継ぎ・監査/361_RD・UI・SSトレーサビリティ.md'];docs={p:doc(p) for p in docNames};designMain=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip();ui233=next(p for p in docs if '/233_' in p);ss323=next(p for p in docs if '/323_' in p);ui=parser.ui_layouts(docs[ui233]);ss=parser.ss_types(docs[ss323]);assert len(ui)==len(ss)==64 and set(ui)==set(ss);fieldDocs={p:t for p,t in docs.items() if any('/'+n+'_' in p for n in ['234','235','236'])};common,specific=parser.ui_field_blocks(fieldDocs);base=r/'src/schubert-nk-protocol/src/test/resources/protocol';layouts=parser.tsv(base/'layouts-ui233.tsv');named=parser.tsv(base/'named-types-ss323.tsv');fields=parser.tsv(base/'fields-ui234-236.tsv');golden=parser.tsv(base/'payload-golden-ui234-236.tsv');assert len(layouts)==len(named)==len(golden)==64 and len(fields)==389;layoutMap={x[0]:x for x in layouts};namedMap={x[0]:x for x in named};goldenMap={x[0]:x for x in golden};assert set(layoutMap)==set(namedMap)==set(goldenMap)==set(ui);namedTypes={n for x in named for n in x[1:] if n!='-'};assert len(namedTypes)==69
fieldMap={}
for line,row in enumerate(fields,1):assert len(row)==8;fieldMap.setdefault((row[0],row[1]),[]).append(dict(oracleRow=line,label=row[2],start=int(row[3]),length=int(row[4]),wire=row[5],presence=row[6],rule=row[7]))
def case(test,method):
 matched=[x for x in cases if x['classname'].split('.')[-1]==test and x['name']==method+'()'];assert len(matched)==1;return matched[0]['classname']+'#'+matched[0]['name']
layoutCases=[case('LayoutMetadataTest','registryMatchesIndependentUi233Catalog'),case('PayloadGoldenVectorTest','allSixtyFourLayoutsMatchIndependentMinimumMaximumAndErrorHashes'),case('PayloadTypeCatalogTest','explicitCatalogMatchesIndependentSs323NamedTypeFixture'),case('PayloadTypeCatalogTest','allSixtyFourLayoutsRoundTripThroughSixtyNineExplicitNamedTypes'),case('PayloadTypeCatalogTest','allNamedTypesHaveIndependentDirectionalFieldMeaning'),case('LayoutFieldCatalogTest','catalogMatchesIndependentUi234To236Fixture')]
classBySimple={Path(p).stem:p for p in cfg['mainSources'] if Path(p).stem!='package-info'};assert namedTypes<=set(classBySimple)
layoutTrace=[];labelAliases=[]
for key in sorted(ui):
 u=ui[key];row=layoutMap[key];assert [u['kind'],u['interaction'],u['data'],u['record'],u['maximum'],u['total']]==[row[1],row[2],*map(int,row[3:])];assert u['total']==256+u['data']+u['record']*u['maximum'];assert ss[key]['lengths']==[u[k] for k in ['data','record','maximum','total']];assert namedMap[key][1:]==[ss[key]['dataType'],ss[key]['recordType']]
 areaRows={}
 for area,length in [('DATA',u['data']),('RECORD',u['record'])]:
  actual=parser.resolve_field_rows(key,area,length,common,specific,fieldDocs);expected=fieldMap.get((key,area),[]);assert [(x['start'],x['length'],x['wire'],x['presence']) for x in actual]==[(x['start'],x['length'],x['wire'],x['presence']) for x in expected]
  for a,x in zip(actual,expected):
   if a['label']!=x['label']:labelAliases.append(dict(layout=key,area=area,uiLabel=a['label'],fixtureLabel=x['label'],start=a['start'],length=a['length'],classification='INTERNAL_FIELD_NAME_ALIAS_SAME_WIRE_OFFSET_TYPE_PRESENCE_NOT_SEMANTIC_EQUIVALENCE_CLAIM'))
  areaRows[area]=dict(uiFields=actual,oracleFields=expected,wireShapeExact=True)
 types=[n for n in namedMap[key][1:] if n!='-'];layoutTrace.append(dict(traceId='G13P-LAYOUT-'+key,layout=key,ui=u,uiSource=ui233,ss=ss[key],ssSource=ss323,types=[dict(name=n,path=classBySimple[n],owner=artifacts[classBySimple[n]]['owner']) for n in types],areas=areaRows,independentGoldenHashes=goldenMap[key][1:],actualJUnitCases=layoutCases,actualExecutionScope='Original same-byte whole152; no per-layout test-count multiplication',businessValidation='Handler/service validation in SS323 is delegated to its owner; wire structural proof does not accept the business operation'))
mainTrace=[];unknown=[]
for cl,p in sorted(mainByClass.items()):
 a=artifacts[p];owner=a['owner'];task=tasks[owner];program=programs[task['program']];related=sorted(set(task['requirementIds'])|set(expand_ids(program['rd'])));assert related and all(x in req for x in related)
 direct=[t for t,text in testTexts.items() if re.search(r'\b'+re.escape(Path(p).stem)+r'\b',text) and casesByTest[t]];sources=direct;via=None;simple=Path(p).stem;classes=[name[:-6] for name,outer in physicalSource.items() if outer==cl];code=sum(raw['classes'][n]['counters']['METHOD']['covered']+raw['classes'][n]['counters']['METHOD']['missed'] for n in classes)
 if simple in namedTypes:links=layoutCases;via='Explicit independent69type/64layout fixture bindings and actual whole named/golden cases'
 elif direct:links=sorted({x for t in direct for x in casesByTest[t]});via='Exact test source type references, static links only; dynamic counters remain whole-run'
 elif code==0:links=[];via='No executable Code; retained physical/package/interface contract and RootNullAway source qualification'
 else:
  callers=[q for q,text in mainTexts.items() if q!=p and re.search(r'\b'+re.escape(simple)+r'\s*\.',text)];sources=[t for t,text in testTexts.items() if any(re.search(r'\b'+re.escape(Path(q).stem)+r'\b',text) for q in callers) and casesByTest[t]];links=sorted({x for t in sources for x in casesByTest[t]});via=dict(kind='Private helper via real source callers',callers=callers)
  if not links:unknown.append(p)
 mainTrace.append(dict(sourcePath=p,currentSha256=now_inputs[p],gitCore=core,canonicalOwner=owner,program=task['program'],programContextRelatedRequirements=related,requirementReferences=[dict(id=i,path=req[i]['source'],text=req[i]['requirement']) for i in related],ssFromOwner=task['ss'],uiFromProgram=program['ui'],physicalClasses=classes,rawCodeMethods=code,actualCaseScopeLinks=links,linkBasis=via,perCaseDynamicAttributionClaimed=False,codeNoMethodsIsNotCoverageExclusion=code==0,independentLayoutLinks=[x['layout'] for x in layoutTrace if any(t['path']==p for t in x['types'])]))
assert not unknown,unknown
methods=[]
for m in raw['methods']:
 outer=m['className'].split('$')[0];p=mainByClass[outer];methods.append(dict(className=m['className'],name=m['name'],descriptor=m['descriptor'],source=p,owner=artifacts[p]['owner'],rawCounters=m['counters'],coveredByOriginalWhole152=m['counters']['METHOD']['covered']>0,perTestProbeAttributionAvailable=False,knownQualityGap='BUG3111/YKT2583' if m['counters']['METHOD']['missed'] or m['counters']['BRANCH']['missed'] else None))
assert len(methods)==1438 and sum(m['rawCounters']['METHOD']['missed'] for m in methods)==4 and sum(m['rawCounters']['BRANCH']['missed'] for m in methods)==58
scopeReq=[]
for key in ['SYS-011','SCP-001','SCP-002','SCP-003','SCP-006']:
 q=req[key];text=doc(q['source']);assert key in text;scopeReq.append(dict(id=key,text=q['requirement'],source=q['source'],sourceSha256=hashlib.sha256(text.encode()).hexdigest(),protocolScope='Lifecycle/contract/source/trace for the protocol slice only; original requirement completion across UI/API/DB/master/runtime remains with original owner',excludedPhysicalAction='No master migration, DB, runtime or IT/ST completion certified'))
# Independent parser negative checks keep duplicate/layout/length loss from looking like a complete audit.
checks=[]
def rejects(label,operation):
 try:operation()
 except (AssertionError,ValueError):checks.append(dict(testId=label,passed=True));return
 raise AssertionError(label+' unexpectedly accepted')
first=next(line for line in docs[ui233].splitlines() if re.search(r'\| [QSE] `[A-Z0-9]{8}`',line));rejects('TRACE-PARSER-DUPLICATE-LAYOUT',lambda:parser.ui_layouts(docs[ui233]+'\n'+first));rejects('TRACE-PARSER-UNKNOWN-LAYOUT',lambda:parser.resolve_field_rows('ZZZREQ01','DATA',1,common,specific,fieldDocs));rejects('TRACE-PARSER-WRONG-LENGTH',lambda:parser.resolve_field_rows('LGNREQ01','DATA',385,common,specific,fieldDocs));rejects('TRACE-PARSER-FALSE-ZERO',lambda:parser.resolve_field_rows('LGNREQ01','DATA',0,common,specific,fieldDocs));assert len(parser.resolve_field_rows('USTREQ01','DATA',60,common,specific,fieldDocs))==5;checks.append(dict(testId='TRACE-PARSER-RESPONSE-ALIAS-NOT-REQUEST-PREFIX',passed=True));assert len(parser.resolve_field_rows('USTRSP01','DATA',24,common,specific,fieldDocs))==3;checks.append(dict(testId='TRACE-PARSER-COMMON-RESPONSE-WITHOUT-OWN-HEADING',passed=True))
out=b/'evidence/PG36800-current-protocol-source-layout-trace-v1';out.mkdir();write=lambda name,value:(out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');write('source-class-owner-requirement-cases.json',mainTrace);write('layout64-fields389-types69.json',layoutTrace);write('physical175-method1438-owner-counters.json',dict(physicalSource=physicalSource,classHashes=physical,methods=methods,knownRawQualityCounters=raw['rawCounterClassSum']));write('requirement-scope-and-parser-canaries.json',dict(requirements=scopeReq,parserCanaries=checks,internalLabelAliases=labelAliases,fieldRulesAreNotClaimedFullyEquivalent=True,flowValidationRemainsWithBusinessOwners=True));write('current-source-reuse.json',dict(sourceCore=core,originalUnit=old['source'],originalCore=old['productionCoreMain'],originalQualifiedPost=ref(postp),rawMeasurement=ref(rawp),allOriginalInputHashes=now_inputs,originalToolHashes=prep['toolHashes'],allPhysicalBytesExact=True,testsReplayed=0,newExecutedPtCount=0,originalExecuted152Unchanged=True,oldExecCombined=False,sourceOnlyMain165Test35Fixture5CountExact=True));write('design-current-pins.json',dict(originMain=designMain,documents={p:hashlib.sha256(t.encode()).hexdigest() for p,t in docs.items()},fixtures=[ref(r/x['path']) for x in cfg['resources']],classModule='protocol',layoutTable64AndIndependentTablesSame=True,wireFields389OffsetLengthTypePresenceSame=True,ruleSemanticEqualityNotInferred=True))
manifest=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=core,originalUnit=old['source'],sourceMain165=165,physical175=175,code162=162,method1438=1438,layout64=64,field389=389,named69=69,uniqueOwners=sorted({x['canonicalOwner'] for x in mainTrace}),unmappedSources=unknown,unmappedPhysical=0,unmappedLayout=0,unmappedMethods=0,parserCanaries6=len(checks),allParserCanariesPassed=True,old152Replayed=0,newProductTests=0,knownMissedMethods4=4,knownMissedBranches58=58,knownQualityIssuesNotClosed=['BUG3111/YKT2583'],currentSourceTraceComplete=True,originalG13ParentAccepted=False,wholeProtocolQualityAccepted=False,whole451Accepted=False,formalUpdated=False,newOriginalAcceptance=0,effortRate=None,files={p.name:sha(p) for p in out.iterdir() if p.is_file()},verifierSource=ref(Path(__file__).resolve()),parserSource=ref(b/'input/4473_protocol_ui_trace_parser.py'));write('manifest.json',manifest);print(json.dumps({k:manifest[k] for k in ['actualExit','sourceMain165','physical175','method1438','layout64','field389','named69','unmappedSources','parserCanaries6','old152Replayed','currentSourceTraceComplete','newOriginalAcceptance']}))
