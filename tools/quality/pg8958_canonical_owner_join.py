"""Current232 ownership correction joins 485 without rewriting historic runs, budgets or source."""
from collections import Counter
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import pg6966_chr_adapter_host as host
import trace_owner_join as resolver
from host_tool_invocation import capture,verify

SOURCE='fb9fce0f91de3d9fdfa634fe277592700f915e45'
INVENTORY=host.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json'
TRACE=host.BASE/'PG8952-web-metric-pipeline-trace-v1/manifest.json'
TRACE_SHA='85aac967c065ccad21eb917a0787fa96fc5bcd8c581bb254738aadccc087e4a0'
NORMAL=host.BASE/'PG8946-web-metric-pipeline-six-compile-v1/manifest.json'
NORMAL_SHA='2bb0684f5eb144957ca69286a703d14fcb19a0fe1826e7621ad496274559b70f'
OUT=host.BASE/'PG8958-canonical-owner-join-v1'

def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def main():
    invocation=capture(Path(__file__))
    assert not OUT.exists() and host.sha(TRACE)==TRACE_SHA and host.sha(NORMAL)==NORMAL_SHA
    trace=json.loads(TRACE.read_text());normal=json.loads(NORMAL.read_text());inventory=json.loads(INVENTORY.read_text())
    assert trace['source']==normal['source']==SOURCE and trace['actualExit']==normal['actualExit']==normal['terminal']['actualExit']==0
    assert trace['allPhysicalClassCount']==1835 and trace['sourceCount']==len(trace['sourceRows'])==232
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT)==b''
    logical={row['path']:row for row in inventory['artifacts']}
    assert len(logical)==len(inventory['artifacts'])==941
    physical={row['path']:row for row in inventory['currentPhysicalCandidate']['artifacts']}
    assert len(physical)==943 and inventory['currentPhysicalCandidate']['source']=='e7d64fda2453e906ee6ccc5fe718e5c29841e4aa'
    hashes=normal['begin']['inputHashes']
    assert all(host.sha(host.ROOT/row['path'])==hashes[row['path']]==row['sha256'] for row in trace['sourceRows'])
    corrected=resolver.join_rows(trace['sourceRows'],logical,hashes,'WBS-P018-09')
    resolver.validate(corrected,trace['sourceRows'],logical,hashes,'WBS-P018-09')
    for row in corrected:
        if row['path'] in logical:
            assert all(logical[row['path']][key]==physical[row['path']][key] for key in ('owner','costOwner'))
    golden={'ApiProcessMain.java':'WBS-P018-05','ApiManagementServer.java':'WBS-P018-05','WebNativeRuntime.java':'WBS-P018-06','WebManagementServer.java':'WBS-P018-06','WebHttpServer.java':'WBS-P018-06'}
    for name,owner in golden.items():
        chosen=[row for row in corrected if Path(row['path']).name==name]
        assert len(chosen)==1 and chosen[0]['canonicalOwner']==chosen[0]['canonicalCostOwner']==owner
        assert chosen[0]['changeOwner']=='WBS-P018-09'
    counts=Counter(row['canonicalOwner'] or 'UNKNOWN' for row in corrected)
    assert counts==Counter({'WBS-P018-09':213,'WBS-C07':8,'WBS-F02':4,'WBS-C02':1,'WBS-C06':1,'WBS-P018-05':2,'WBS-P018-06':3})
    changed=[dict(path=row['path'],legacyReportedOwner=row['legacyReportedOwner'],canonicalOwner=row['canonicalOwner'],canonicalCostOwner=row['canonicalCostOwner'],changeOwner=row['changeOwner']) for row in corrected if row['legacyReportedOwner']!=row['canonicalOwner']]
    assert len(changed)==19 and all(row['ownershipStatus']!='UNKNOWN' for row in corrected)
    unknown=resolver.canonical('src/unclassified/Unknown.java',logical)
    assert unknown['ownershipStatus']=='UNKNOWN' and unknown['canonicalOwner'] is unknown['canonicalCostOwner'] is None
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,source=SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,bug='BUG-1725',ykt='YKT-1476',rawTraceSha256=TRACE_SHA,normalManifestSha256=NORMAL_SHA,inventoryFileSha256AtJoin=host.sha(INVENTORY),logicalInventoryDatasetSha256=digest(inventory['artifacts']),historicalPhysicalDatasetSha256=digest(inventory['currentPhysicalCandidate']),historicalPhysicalSource=inventory['currentPhysicalCandidate']['source'],historicalPhysicalNotCurrentPt=True,canonicalRuleSha256=host.sha(Path(resolver.__file__)),baselineKnown=5,newLogicalCandidates=227,unknown=0,canonicalOwnerCounts=dict(counts),differingLegacyOwnerLabels=changed,sourceRows=corrected,sourceCount=232,allPhysicalMain=1835,productTestsExecuted=0,coverage=None,rawTraceExecutionReplayed=False,formalUpdated=False,newAccepted=0,effortPercent=None,historicalBudgetsOrCostsReallocated=False,historicalEventsModified=False,currentWholeSourceQualified=False,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0)
    host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rows=232,baselineKnown=5,newLogicalCandidates=227,unknown=0,canonicalOwnerCounts=dict(counts),differentLegacyOwner=19,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':
    main()
