"""Independent current Inbox15/full14Source: nine four100/three natural/two gaps, old history retained."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg15684_current1973_pre_sql_registry import SOURCE,PREV,PREV_POST,POST,INDEPENDENT,read,require

PIN='34ab91df2ee7ec004ae0bf4dc0d7cc4319f5ec859180fa6f7151f2f81312be62'
OUT=data.BASE/'PG15687-current1973-pre-sql-registry-post-v2'

def wire(v):return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(isinstance(PIN,str) and len(PIN)==64 and all(c in '0123456789abcdef' for c in PIN),'bound literal digest');require(data.sha((data.ROOT/'tools/quality/pg15686_current1973_pre_sql_registry_post.py').read_bytes())=='2c1094ca80537b35e598a3b82c26192a9cf7e5ec5310bb5de3dffb62b8814ba8','old failure unchanged');require(not OUT.exists(),'new-only1711 independent registry')
    old,prior,m=[read(pair) for pair in [PREV,PREV_POST,('PG15684-current1973-pre-sql-registry-v1',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,m]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34,'genuine independently qualified914 predecessor')
    methods={(c['classname'],c['name']) for c in old['cases']};units=copy.deepcopy(old['fullSourceUnits']);owners=copy.deepcopy(old['owners']);refs=copy.deepcopy(old['originalPostReferences']);witnesses=[];metadata=copy.deepcopy(old['metadataClasses'])
    p,proof=read(POST),read(INDEPENDENT);witnesses.extend([p,proof])
    require(p['actualExit']==proof['actualExit']==0 and p['source']==proof['source']==SOURCE and proof['postSha256']==POST[1] and proof['semanticNegativeVectors']==32 and proof['tests']==13,'genuine independent original13')
    require(proof['independentNpeAssertionCounts']==dict(LogQueryPreSqlBoundaryTest=3,QuestionQueryPreSqlBoundaryTest=12,UserQueryPreSqlBoundaryTest=8) and proof['zeroJdbcAssertionCounts']==dict(LogQueryPreSqlBoundaryTest=3,QuestionQueryPreSqlBoundaryTest=6,UserQueryPreSqlBoundaryTest=4),'independent null and zero-call assertions')
    require(p['sameExecMeasurementSupplementalOnly'] is proof['sameExecMeasurementSupplementalOnly'] is proof['previousProofsNotReplaced'] is True and p['currentSourceQualificationProofsReplaced'] is proof['currentSourceQualificationProofsReplaced'] is p['actualJdbcBackendConnected'] is proof['actualJdbcBackendConnected'] is p['cryptoOrKeyOperationsInvoked'] is proof['cryptoOrKeyOperationsInvoked'] is False,'supplement only/no backend or crypto')
    require(all(p[k]==proof[k]==0 for k in ['actualJdbcMethodsInvoked','actualSqlStatementsPreparedOrExecuted','newAccepted']) and p['singleSession'] is True and p['crcMismatch']==0 and p['strictFour100GateExit']==1,'no current source-wide pass')
    require(proof['newSourcePrograms']==0 and set(proof['previousSourceProofs'])==set(p['fullSourceUnits']) and all(units[n]==u for n,u in proof['previousSourceProofs'].items()),'all existing three Source proofs unchanged')
    require(p['metadataClasses']==['dev/codex/schubert/nk/api/persistence/QuestionQueryRepository$RowMapper'] and all(metadata[n]['sha256']==p['sourcePhysicalInventory'][n]['sha256'] for n in p['metadataClasses']),'existing NoCode not recounted')
    new={(c['classname'],c['name']) for c in p['cases']};require(len(new)==13 and not new&methods and all(c['result']=='PASS' for c in p['cases']),'new disjoint thirteen');methods|=new
    for path,row in p['owners'].items():
        require(path not in owners or owners[path]==row,'existing roles unchanged');owners[path]=copy.deepcopy(row)
    refs.append(dict(name=POST[0],sha256=POST[1],tests=13,suites=3,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='ORIGINAL_PRE_SQL13_SUPPLEMENTAL_MEASUREMENT_NO_SOURCE_REPLACEMENT'))
    scope_refs=copy.deepcopy(old['additionalScopeReferences'])
    scope_refs.append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),newTests=13,newExecs=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='SUPPLEMENTAL_WHOLE_BOUNDARY_MEASUREMENT_NOT_SOURCE_QUALIFICATION_REPLACEMENT',existingSourceNames=sorted(p['fullSourceUnits']),existingSourceQualificationPreserved=True,coverageExecUnion=False))
    cases=[dict(classname=c,name=n) for c,n in sorted(methods)];physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};meta=metadata
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'all302 complete Source closures disjoint')
    incomplete={n for n,u in units.items() if not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly'])}
    require(len(incomplete)==old['incompleteSourcePrograms']==17 and len({n for name in incomplete for n in units[name]['physical']})==28,'new measured incomplete partition explicit, no gate relaxation')
    summary=copy.deepcopy(prior['summary']);summary.update(metadataPhysical=len(metadata),incompleteSourcePrograms=len(incomplete),tests=len(cases),suites=len({c['classname'] for c in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+13,uniqueProductMethodDelta=13,newTestIds=13,sourceProgramDelta=0,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len({n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']}),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in owners.values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in owners.values()))
    require((summary['tests'],summary['suites'],summary['measuredSourcePrograms'],summary['measuredPhysical'],summary['executablePhysical'],summary['four100SourcePrograms'],summary['four100Physical'],summary['four100ExecutablePhysical'],summary['totalProductExecs'],summary['totalMethodExecutions'],summary['naturalZeroBranchSourcePrograms'],summary['naturalZeroBranchPhysical'],summary['metadataSourcePrograms'],summary['incompleteSourcePrograms'])==(1973,256,438,575,554,243,355,344,109,2081,172,186,6,17),'exact independent category/method/JVM counts')
    require(summary['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':353,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':227,'UNKNOWN':140},'actual owners distinct from change group; UNKNOWN retained')
    changed={'lastUpdateKind','invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','fullSourceUnits','owners','originalPostReferences','additionalScopeReferences','metadataClasses',*summary}
    def contract(v):
        require(v['lastUpdateKind']=='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_WITH_DISCLOSURE_HISTORY_RETAINED' and v['postDisclosureCorrections']==old['postDisclosureCorrections'],'new PT marker and all previous digest errata retained')
        require(all(wire(v[k])==wire(value) for k,value in summary.items()),'all independently derived typed counts')
        require(v['cases']==cases and v['suiteNames']==sorted({c['classname'] for c in cases}) and wire(v['fullSourceUnits'])==wire(units) and v['owners']==owners and wire(v['originalPostReferences'])==wire(refs),'all actual old/new cases/whole proof/owner roles')
        require(wire(v['additionalScopeReferences'])==wire(scope_refs),'separate supplemental refs without replacement');require(wire(v['metadataClasses'])==wire(metadata) and v['metadataPhysical']==21,'new explicit NoCode interface and all old metadata retained')
        require(v['previousUniqueRegistryReference']==list(PREV) and v['previousRegistryPostReference']==list(PREV_POST),'exact immutable predecessor')
        require(all(wire(v[k])==wire(value) for k,value in old.items() if k not in changed),'old Catalog/SQLjoint/JS/metadata/cost/formal untouched')
    contract(m);negative=[]
    for key,value in [('tests',914),('suites',132),('totalProductExecs',61),('totalMethodExecutions',994),('totalRepeatedOriginalMethods',92),('uniqueProductMethodDelta',0),('sourceProgramDelta',1),('four100SourcePrograms',131),('four100Physical',196),('incompleteSourcePrograms',4),('naturalZeroBranchSourcePrograms',145),('measuredSourcePrograms',287),('measuredPhysical',365),('executablePhysical',347),('metadataPhysical',0),('metadataSourcePrograms',0),('fullSourceUnits',{}),('metadataClasses',{}),('cases',old['cases']),('originalPostReferences',old['originalPostReferences']),('qualificationReplacedUnitHistory',{}),('jointQualificationReplacedUnitHistory',{}),('javascriptResourceDomain',{}),('unknownOwnerPaths',99),('ownerStatusCounts',{'BASELINE_LOGICAL_REFERENCE':283,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':80,'UNKNOWN':103}),('priorSource0061TestsTransferred',True),('coverageExecUnion',True),('formalUpdated',True),('newAccepted',1),('effortPercent',75),('uniqueProductMethodDelta',True)]:
        bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false1697 registry accepted '+key)
    for label in ['typed-counter-bool','typed-four100-int','typed-suite-bool']:
        bad=copy.deepcopy(m)
        if label=='typed-counter-bool':
            next(iter(bad['fullSourceUnits'].values()))['counters']['LINE']['missed']=False
        elif label=='typed-four100-int':
            unit=next(u for u in bad['fullSourceUnits'].values() if u['four100'] is True);unit['four100']=1
        else:
            reference=next(r for r in bad['originalPostReferences'] if r['suites']==1);reference['suites']=True
        try:contract(bad)
        except ValueError:negative.append(label)
        else:raise ValueError('numeric and boolean roles must not alias '+label)
    for v in [old,prior,m,*witnesses]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,summary=summary,metadataNegativeVectors=len(negative),negativeLabels=negative,allOldCasesAndSourceProofsPreserved=True,newSourcePrograms=0,newUniqueMethods=13,newIncompleteSources=0,newIncompletePhysical=0,incompletePhysicalClasses=28,newProductExecutions=1,protocolMainSourceCount=158,protocolNormalMainSourceInventoryMatched=True,originalMethodsReexecutedByRegistry=0,coverageExecUnion=False,actualBackupOrToolAuthorityVerified=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
