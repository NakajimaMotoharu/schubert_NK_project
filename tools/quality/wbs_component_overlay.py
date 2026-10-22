"""Explicit technical common-tool overlay; never relabel the six-module run."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]
BASE='evidence/01_PT/018_NK-OPS-001/evidence/provisional/'
SOURCE='3c70db39377cee751d7ecd12bb439c447e0c61c0'
DECLARATION=dict(version=1,component='characterization-common-four-main',source=SOURCE,
                bindingPath=BASE+'PG6984-chr-adapter-acceptance-v1/manifest.json',
                bindingSha256='acfd9e9c20c8acbb80c63dff96fd21d5c8bde8c1caa8e3f6a09fb8cb34f572e3',
                qualificationPath=BASE+'PG6980-chr-path-qualification-v1/manifest.json',
                qualificationSha256='0bbc80f788ac9c26caada7f363415a803aa6cef3796222d519467d6d60e34631')
FROZEN='9d2b93aef'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value,message):
    if not value:raise ValueError(message)


def verify(candidate):
    declaration=candidate.get('componentOverlay')
    if declaration is None:return {},None
    require(declaration==DECLARATION,'only exact explicit qualified common overlay, no arbitrary exemption')
    for p,h in ((declaration['bindingPath'],declaration['bindingSha256']),
                (declaration['qualificationPath'],declaration['qualificationSha256'])):
        require(sha(ROOT/p)==h,'real immutable overlay evidence')
    binding=json.loads((ROOT/declaration['bindingPath']).read_bytes())
    q=json.loads((ROOT/declaration['qualificationPath']).read_bytes())
    require(binding['source']==q['source']==SOURCE and q['actualExit']==0 and q['tests']==44
            and q['physicalMain']==8 and q['crcClassMismatch']==0 and q['actualSessionCount']==1
            and q['originalBaselineUnchanged'] and binding['qualifiedProductionSource']==candidate['source'],
            'independent actual common source/CRC/session, no production source laundering')
    rows=[a for a in candidate['artifacts'] if a['owner']=='WBS-P020-01']
    expected={a['path']:a for a in rows}
    overlay=binding['componentScopeOverlay']
    require(set(expected)==set(overlay) and len(rows)==len(expected)==4,'exact declared four parent Main, no missing/extra/duplicate')
    hashes={}
    for path,row in overlay.items():
        require(row['priorSha256']==expected[path]['sha256'] and row['owner']=='WBS-P020-01'
                and row['additionalBudgetPp']==0 and row['source']==SOURCE,'old/new byte lineage and fixed owner/cost')
        raw=subprocess.check_output(['git','show',SOURCE+':'+path],cwd=ROOT)
        require(hashlib.sha256(raw).hexdigest()==q['sourceInputs'][path]==row['currentSha256']==sha(ROOT/path),
                'every current physical Main exact original source')
        hashes[path]=row['currentSha256']
    require(not subprocess.check_output(['git','diff',candidate['source'],SOURCE,'--','src','pom.xml','.mvn','mvnw','tools/quality/static'],cwd=ROOT),
            'all original six-module inputs unchanged, not a new six-module success')
    require(not subprocess.check_output(['git','diff',SOURCE,'--','program/characterization'],cwd=ROOT),
            'no common source drift after its exact qualified run')
    for path,h in q['sourceInputs'].items():require(sha(ROOT/path)==h,'all original common Test/fixture/pom bytes')
    require(all(v['missed']==0 and v['covered']>0 for v in q['counters'].values()),'actual common counters, no synthetic100')
    result=dict(component=declaration['component'],source=SOURCE,run=q['sourceRun'],tests=44,suites=5,
                physicalMain=8,counters=q['counters'],crcMismatch=0,sessions=1,physicalArtifacts=4,
                changedPhysicalMain=sum(row['priorSha256']!=row['currentSha256'] for row in overlay.values()),
                originalSixSource=candidate['source'],originalSixRunRelabelled=False,coverageUnion=False,
                acceptedLeafDelta=0,formalAccepted=False,effortPercent=None)
    return hashes,result


def historical_state_unchanged(pmo,hashes):
    """Keep immutable old acceptance snapshots while only declared trace pointers evolve."""
    for name,h in hashes.items():
        if sha(pmo/name)==h:continue
        require(name in ('485_WBS網羅性・受入対応.json','486_WBS現行実績.json'),'logical criteria/budget/source/acceptance immutable')
        raw=subprocess.check_output(['git','show',FROZEN+':'+str((pmo/name).relative_to(ROOT))],cwd=ROOT)
        require(hashlib.sha256(raw).hexdigest()==h,'old acceptance really bound to saved original bytes')
        before=json.loads(raw);after=json.loads((pmo/name).read_bytes())
        if name.startswith('485_'):
            require(after['currentPhysicalCandidate'].get('componentOverlay')==DECLARATION,'only declared overlay field changes')
            copy_after=copy.deepcopy(after);copy_after['currentPhysicalCandidate'].pop('componentOverlay')
            require(copy_after==before,'entire historical/logical inventory remains exact')
            verify(after['currentPhysicalCandidate'])
        else:
            new=copy.deepcopy(after)
            require(new['inventorySha256']==sha(pmo/'485_WBS網羅性・受入対応.json'),'current inventory pointer exact')
            new['inventorySha256']=before['inventorySha256']
            measure=new['currentPhysicalCandidateMeasurement'];extra=measure.pop('componentOverlay')
            candidate=json.loads((pmo/'485_WBS網羅性・受入対応.json').read_bytes())['currentPhysicalCandidate']
            require(extra==verify(candidate)[1],'current technical overlay result exact')
            require(new==before,'historical17/source/counter/budget never rebound')
    return True
