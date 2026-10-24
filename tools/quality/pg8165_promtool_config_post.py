"""Independent read-only qualification of original owned promtool syntax receipts, no child jobs."""
import copy
import datetime
import hashlib
import json
from pathlib import Path
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg8164-promtool-config-pt-v1')
RAW=BASE/'PG8164-promtool-config-pt-v1/manifest.json'
PREP=BASE/'PG8162-promtool-prepare-v1/manifest.json'
OUT=BASE/'PG8165-promtool-config-post-v1'
RAW_SHA='df069f5ee7e017bfce8187af2d7c3bed2363a86f1483ded51fc55ef3b9e4b7b6'
PREP_SHA='ca3c93186503b91ff14183b1759b7c8b1e0e33fc73d16685974a8ebd2a01ecae'
BINARY=Path('/home/mini/codex/project1/work/toolchain/promtool-3.13.5-linux-amd64/promtool')
BINARY_SHA='4e84296dc89ef03d856674d76d387f5ccc54a698136c2f0dc30ceef2286908ff'
NAMES=('debug.yml','standard.yml','unknown-field.yml','timeout-greater-interval.yml','duplicate-job.yml')


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()


def require(value):
    if not value:
        raise ValueError('exact original source, command, fixed oracle and genuine result required')


def assess(raw):
    require(raw['actualExit']==0 and raw['tests']==6 and raw['failed']==raw['errors']==raw['skipped']==0)
    require(raw['source']=='941bd89d15da0d37c2023c7ce9536b9845311779')
    require(raw['syntaxProcesses']==5 and raw['exactOneInvocationPerSyntaxCase'] is True)
    require(raw['actualScrapes']==raw['targetNetworkActions']==raw['actualDaemonActions']==0)
    require([r['testId'] for r in raw['cases']]==[f'PROMTOOL{n:03d}' for n in range(1,7)])
    for n,row in enumerate(raw['cases']):
        expected=0 if n<3 else 1
        require(row['expectedExit']==row['actualExit']==expected and row['result']=='PASS')
        if n:
            require(row['command']==[str(BINARY),'check','config','--syntax-only',str(W/NAMES[n-1])])
            require(row['input']['sha256']==raw['fixtureHashes'][NAMES[n-1]])
    for key in ('whole451Accepted','formalUpdated'):
        require(raw[key] is False)
    require(raw['newAccepted']==0 and raw['effortPercent'] is None)


def main():
    invocation=capture(Path(__file__))
    require(not OUT.exists())
    require(sha(RAW)==RAW_SHA and sha(PREP)==PREP_SHA and sha(BINARY)==BINARY_SHA)
    raw=json.loads(RAW.read_bytes())
    prep=json.loads(PREP.read_bytes())
    assess(raw)
    require(prep['actualExit']==0 and prep['toolOnly'] is True and prep['unselectedMembersExtracted']==0)
    require(raw['originalPreparation']['sha256']==PREP_SHA and raw['originalPreparation']['versionRerun'] is False)
    require(all(sha(ROOT/p)==h for p,h in raw['inputHashes'].items()))
    require(all(sha(W/p)==h for p,h in raw['fixtureHashes'].items()))
    for n,row in enumerate(raw['cases'][1:],2):
        actual=json.loads((W/f'PROMTOOL{n:03d}.safe.json').read_bytes())
        require(actual==row)
    rejected=[]
    for name,change in (
        ('unknown-result',lambda x:x.update(actualExit=None)),
        ('skipped',lambda x:x.update(skipped=1)),
        ('negative-to-success',lambda x:x['cases'][3].update(expectedExit=0,actualExit=0)),
        ('different-source',lambda x:x.update(source='other')),
        ('network-command',lambda x:x['cases'][1].update(command=[str(BINARY),'query','instant'])),
        ('scope-inflation',lambda x:x.update(whole451Accepted=True))):
        candidate=copy.deepcopy(raw)
        change(candidate)
        try:
            assess(candidate)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('independent original evidence mutation must refuse')
    verify(invocation)
    value=dict(actualExit=0,source=raw['source'],invocation=invocation,
        timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        originalManifestSha256=RAW_SHA,originalPreparationSha256=PREP_SHA,binarySha256=BINARY_SHA,
        actualTests=6,syntaxProcesses=5,negativeOracleCases=3,negativeReceiptGuards=rejected,
        originalSourceAndFixtureHashesUnchanged=True,actualChildJobsIssued=0,targetNetworkActions=0,
        actualVmActions=0,actualDatabaseActions=0,actualDaemonActions=0,formalUpdated=False,
        newAccepted=0,effortPercent=None,whole451Accepted=False)
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2)
        f.write('\n')
    print(json.dumps(dict(actualExit=0,tests=6,negativeGuards=len(rejected),manifestSha256=sha(OUT/'manifest.json'))))

if __name__=='__main__':
    main()
