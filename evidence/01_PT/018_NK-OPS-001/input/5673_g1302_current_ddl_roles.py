import hashlib,json,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
ops=Path('evidence/01_PT/018_NK-OPS-001/evidence')
def locate(n,name='manifest.json'):
    return next(ops.glob('PG'+str(n)+'*/'+name))
def load(p):
    return json.loads(p.read_bytes())
def pin(p):
    return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def git(*args):
    return subprocess.check_output(['git',*args])
prior=locate(26124)
old=load(prior)
base=Path('src/schubert-nk-api/src/main/resources/db')
sources=sorted((base/'migration').glob('V*.sql'))+sorted((base/'provisioning').glob('*.sql'))
assert len(sources)==31
versions=[re.match(r'V(\d{3})__.+\.sql$',p.name).group(1) for p in sources if p.parent.name=='migration']
assert versions==[f'{n:03}' for n in range(1,31)]
control=locate(26124,'artifact-owner-testid-candidates.json')
assert old['files'][control.name]==pin(control)['sha256']
authority_rows={x['path']:x for x in load(control) if x['sqlResource']}
assert len(authority_rows)==29
head=git('rev-parse','HEAD').decode().strip()
core='2611e1acbd57955d591d52e5348999ea293e068d'
for path, row in authority_rows.items():
    p=Path(path)
    assert p in sources and pin(p)['sha256']==row['sha256'] and git('show',f'{core}:{p}')==p.read_bytes()
new_only=set(sources)-set(map(Path,authority_rows))
assert {p.name.split('__')[0] for p in new_only}=={'V029','V030'}
migration29=next(p for p in sources if p.name.startswith('V029__'))
migration30=next(p for p in sources if p.name.startswith('V030__'))
rollback=Path('src/deployment/migration/030_audio_role_rollback.sql.template')
role=base/'provisioning/001_roles.sql'
typed=Path('src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/database')
version_test=typed/'MigrationInventory.java'
filename_test=typed/'DatabaseMigrationTest.java'
assert re.findall(r'"([0-9]{3})"',version_test.read_text())==versions
fixture=filename_test.read_text().split('void sqlResourcesContainNoCredentialOrUnsafeBytes()',1)[1].split('\n  }',1)[0]
expected=set(re.findall(r'"((?:migration|provisioning)/[A-Za-z0-9_.-]+\.sql)"',fixture))
assert expected=={p.relative_to(base).as_posix() for p in sources}
assert all(git('show',f'{head}:{p}')==p.read_bytes() for p in (version_test,filename_test))
records29=locate(29714)
static29=load(records29)
assert static29['actualExit']==0
records30=locate(32654)
static30=load(records30)
assert static30['actualExit']==0 and static30['sqlStatementsUnchangedFromIndependentGolden']
for p in (migration30,rollback):
    assert pin(p)['sha256']==static30['currentDdlArtifacts'][str(p)]['sha256']
assert not git('diff','--name-only',old['source'],core,'--',*map(str,set(sources)-new_only))
ddl29=migration29.read_text()
assert ddl29.count(') IS TRUE')==5 and len(re.findall(r'^ALTER TABLE\s',ddl29,re.M))==4
assert 'SET ROLE nk_owner;' in ddl29 and 'RESET ROLE;' in ddl29
ddl30=migration30.read_text()
undo=rollback.read_text()
assert 'varchar(11)' in ddl30 and 'BETWEEN 1 AND 11' in ddl30
assert all(fragment in undo for fragment in ('ACCESS EXCLUSIVE MODE','octet_length(audio_role) > 8','varchar(8)','BETWEEN 1 AND 8'))
assert 'WITH ADMIN FALSE, INHERIT FALSE, SET TRUE;' in role.read_text()
canonical=git('rev-parse','origin/main').decode().strip()
ss=next(Path('documents/300_SS').glob('*/343_*.md'))
rd=next(Path('documents/300_SS').glob('*/331_*.md'))
formal_ddl=git('show',f'{canonical}:{ss}').decode()
assert all(x in formal_ddl for x in ('V030__preserve_current_audio_role.sql','Flyway','schubert_migration'))
assert '限定' in git('show',f'{canonical}:{rd}').decode()
assert git('diff','--name-only',core,head,'--',*(map(str,[*sources,rollback])))==b''
scope=[]
for p in [*sources,rollback]:
    if p in (migration29,migration30,rollback):
        role='WBS-P004-01'
        line='SSC340 / PT-DB-NULL340-001..015' if p==migration29 else 'SSC396 / PT-DB-AUDIOROLE030'
    else:
        role=authority_rows[str(p)]['owner']
        line='inherited exact owner and historical Test IDs PG26124'
    scope.append(dict(source=pin(p),owner=role,oracleEvidence=line,
        upToDateSourceInventory=True,runtimeConformanceVerified=False))
out=ops/'PG41428-g1302-current-ddl-role-trace-v1'
out.mkdir()
result=dict(run=out.name,actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),source=head,productionCore=core,
    legacySqlByteEqual=29,forwardMigrations=30,provisioningScripts=1,cutbackTemplates=1,
    migrationVersionsFromIndependentTest=versions,filenameOracle=pin(filename_test),versionOracle=pin(version_test),
    currentSqlScope=scope,canonicalDesignSource=canonical,oldTrace=pin(prior),
    deltaAuthority=[pin(records29),pin(records30)],databaseSqlExecution=0,testSourcesCompiled=0,newProductTests=0,
    actualRoleStateObserved=False,required=['same-source migration/rollback, current role proof and real DB postconditions','approved actual DAO and complete 451'],
    remainingV030OperationHeld=True,addedOriginalCostPp=0,formalDelta=0,wholeG1302=False)
(out/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(len(scope),len(versions),len(authority_rows))
