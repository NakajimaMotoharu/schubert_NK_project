"""Storage module plus cross-module persistence candidate trace, no SQL/JDBC/native execution."""
from pathlib import Path
import collections,datetime as dt,hashlib,json,re,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG26124-g1302-storage-persistence-trace-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text())
D=R/'documents/400_PGPT/470_PMO';inv=load(D/'485_WBS網羅性・受入対応.json');w=load(D/'481_PGPT詳細WBS.json');tasks={x['id']:x for x in w['tasks']};descriptor=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22122-current7aed-lineage-style-v1/artifacts.json';assert sha(descriptor)=='fb24a1a209849d42894925002baae668bc55a4bd858b1b7c1d38ab838319bb0b';current={x['path']:x for x in load(descriptor)}
markers={'jdbc_import':r'(?m)^import java\.sql\.','connection_api':r'\b(?:prepareStatement|prepareCall|createStatement|getConnection|setAutoCommit|executeQuery|executeUpdate)\s*\(','repository_type':r'\b(?:interface|class|record)\s+\w*(?:Repository|DataSource|Transaction)\b'}
selected=[];candidateCount=0;mainScanned=0;unowned=[];ownerIds=set();sql=[]
for row in current.values():
 name=row['path'];p=R/name;isStorage='/schubert-nk-storage/' in name;isSql=name.endswith('.sql');isMain='/src/main/java/' in name and name.endswith('.java');hits=[];text=None
 if isMain:
  mainScanned+=1;text=p.read_text();hits=[k for k,pattern in markers.items() if re.search(pattern,text)]
 if not (isStorage or isSql or hits):continue
 assert name in current and sha(p)==current[name]['sha256']
 owner=row.get('owner');ownerIds.add(owner)
 if owner not in tasks:unowned.append(dict(path=name,owner=owner))
 if text is None:text=p.read_text()
 ids=sorted(set(re.findall(r'\bPT[-_][A-Z0-9][A-Z0-9_-]*',text)))
 candidateCount+=bool(hits);v=dict(path=name,sha256=sha(p),kind=row['kind'],module=(re.search(r'/schubert-nk-([^/]+)/',name).group(1) if '/schubert-nk-' in name else 'characterization'),owner=owner,costOwner=row.get('costOwner'),storageModule=isStorage,sqlResource=isSql,logicalPersistenceMarkers=hits,testIdMentions=ids,oracleOrRuntimeAccepted=False)
 if isSql:
  patterns={'table':r'\bCREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([\w.]+)','schema':r'\bCREATE\s+SCHEMA\s+(?:IF\s+NOT\s+EXISTS\s+)?([\w.]+)','index':r'\bCREATE\s+(?:UNIQUE\s+)?INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?([\w.]+)','function':r'\bCREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+([\w.]+)'}
  v['sourceDeclarations']={k:re.findall(pattern,text,re.I) for k,pattern in patterns.items()};sql.append(v)
 selected.append(v)
assert mainScanned==972 and len(sql)==29 and not unowned
migrations=[v for v in sql if '/migration/' in v['path']];versions=sorted(int(re.search(r'/V(\d+)__',v['path']).group(1)) for v in migrations);assert versions==list(range(1,29));assert len([x for x in sql if x['kind']=='ROLE_SQL'])==1
storage=[x for x in selected if x['storageModule']];assert len(storage)==25
requirements=[]
for row in inv['requirements']:
 if row['owner'] not in ownerIds and row['id'] not in ['SYS-011','SCP-001','SCP-002','SCP-003','SCP-006']:continue
 assert row['requirement'] in (R/row['source']).read_text().splitlines()[row['line']-1];requirements.append(dict(id=row['id'],source=row['source'],line=row['line'],expected=row['requirement'],owner=row['owner'],accepted=False))
ownerTrace=[]
for id in sorted(ownerIds):
 row=tasks[id];ownerTrace.append(dict(id=id,title=row['title'],relatedRD=row['rd'],relatedUI=row['ui'],ss=row['ss'],requirementIds=row['requirementIds'],candidateTestFiles=row['evidencePlan']['candidateTestFiles'],specDirectory=row['evidencePlan']['specDirectory'],existingAcceptanceSource=row['acceptance'].get('source'),dependencies=row['dependencies'],selectedArtifacts=[x['path'] for x in selected if x['owner']==id],oracleCoverageVerified=False))
counts={k:sum(len(v['sourceDeclarations'][k]) for v in sql) for k in ['table','schema','index','function']};assert counts==dict(table=24,schema=2,index=45,function=42)
# Lexical candidates include interfaces/validators and can over-select; they do not certify semantic DAO completeness.
assert not O.exists();O.mkdir();(O/'artifact-owner-testid-candidates.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n');(O/'owner-requirement-test-plan.json').write_text(json.dumps(ownerTrace,ensure_ascii=False,indent=2)+'\n');v=dict(actualExit=0,atJST=dt.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),productionCoreMain='7aed8eace7c844c2f79f2e39db766faf914890d5',scannedMainJava=mainScanned,storageModuleArtifacts=25,logicalPersistenceCandidates=candidateCount,selectedArtifacts=len(selected),selectedOwners=len(ownerTrace),unownedArtifacts=unowned,SQLresources=29,migrationVersions=versions,provisioningResources=1,SQLsourceDeclarationCounts=counts,SQLCountsAreNotFinalDatabaseState=True,requirements=requirements,allOracleBranchesIndividuallyVerified=False,allDAOClassificationsSemanticallyVerified=False,productTestsExecuted=0,sqlParsersOrDatabaseCommandsExecuted=0,nativeOperations=0,heldClassFileReads=0,rootTwoTestFileReads=0,newAcceptance=0,formalUpdated=False,effortRate=None,wholeG1302Accepted=False,missingConditions=['Logical persistence lexical candidate classification is not complete per-method DAO/SQL independent postcondition audit.','24 table/45 index/42 CREATE-function declarations are source counts including historical redefinitions; do not substitute them for effective DDL/role/constraint postconditions.','Current SQL role/transaction/inbox/outbox schema/run and native permission/FD IO execution remain with each existing B/N owner and HOLD.','Owner candidate Test files and JavaDoc TestID mentions need individual independent expected-result and actual normal proof binding, not presence-based acceptance.'],files={p.name:sha(p) for p in O.iterdir()},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,mainScanned=mainScanned,artifacts=len(selected),owners=len(ownerTrace),SQLresources=29,logicalCandidates=candidateCount,sha256=sha(O/'manifest.json'))))
