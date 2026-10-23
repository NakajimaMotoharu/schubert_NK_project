"""Public same-byte source/TestID/artifact delta trace, not a new whole-source PASS."""
import datetime
import json
import os
import subprocess
from pathlib import Path

import pg6966_chr_adapter_host as host

SOURCE = '6ebb81e1173e001a627374b533b34766b44785b0'
ORIGINAL = 'e7d64fda2453e906ee6ccc5fe718e5c29841e4aa'
OUT = host.BASE/'PG7052-monitoring-addition-trace-v1'
PINS = {
 'PG7046-monitoring-status-post-v1':'bdee1eecf46db2f6df358c80c344d12e04463414d09e9cc1c77e8068bd62ea74',
 'PG7050-monitoring-status-six-post-v1':'740a1e6cecdc2a732ed0c32ed509ff1e8a76de694d3214de93310bb63a583d3f',
 'PG7038-c02-four-template-post-v1':'86e8d32bf2b07f73bb57e727be495f1f27b190a58979f872c50c848cfd22d9ef',
 'PG7042-c06-config-template-post-v1':'8866f08d6f317aca3ebd75415ca8ee2b9ca2b28c3762675aa95648375ec73250'}
CONTRACTS = {
 'MonitoringModePolicy':('MONMODE001..007',1541,1542),
 'MetricContract':('METRIC001..006',1543,1544),
 'AlertLifecycle':('ALERT001..010',1545,1546),
 'AlertRegistry':('ALERTREG001..004',1545,1546),
 'AlertThresholds':('THRESH001..014',1547,1548),
 'ObservationContext':('MONPIPE001..007',1549,1550),
 'MonitoringPolicyEngine':('MONPIPE001..007',1549,1550),
 'MonitoringStatusText':('MONSTATUS001..006',1558,1559)}


def require(value, message):
    if not value:
        raise ValueError(message)


def main():
    require(not OUT.exists(),'new-only trace publication')
    witnesses={}
    for label,digest in PINS.items():
        path=host.BASE/label/'manifest.json'
        require(host.sha(path)==digest,'pinned original post, no replay')
        witnesses[label]=json.loads(path.read_bytes())
    component=witnesses['PG7046-monitoring-status-post-v1']
    physical=witnesses['PG7050-monitoring-status-six-post-v1']
    require(component['source']==physical['source']==SOURCE and component['tests']==54
            and component['actualCrcMismatch']==0 and physical['existingChangedClassCount']==0,
            'exact54 source and old physical bytes, no cross-source inferred result')
    documents={}
    for path in (host.ROOT/'evidence/01_PT/018_NK-OPS-001').glob('*.md'):
        prefix=path.name.partition('_')[0]
        if prefix.isdigit():documents[int(prefix)]=path
    rows=[]
    for delta in physical['newSourceDelta']:
        path=host.ROOT/delta['path'];stem=path.stem
        raw=subprocess.check_output(['git','show',SOURCE+':'+delta['path']],cwd=host.ROOT)
        require(host.sha(path)==delta['sha256'] and __import__('hashlib').sha256(raw).hexdigest()==delta['sha256'],
                'each current source byte equals exact qualified candidate')
        if delta['owner']=='WBS-P018-09':
            if stem=='package-info':
                ids='MONMODE/METRIC/ALERT/ALERTREG/THRESH/MONPIPE/MONSTATUS';spec,result=1558,1559
                kind='NULLABILITY_METADATA_NOT_EXECUTABLE'
            else:
                key='MetricContract' if stem=='metric-catalog' else stem.removesuffix('Test')
                ids,spec,result=CONTRACTS[key]
                kind='INDEPENDENT_GOLDEN_RESOURCE' if path.suffix=='.tsv' else 'TEST' if stem.endswith('Test') else 'MAIN'
        else:
            require(stem in ('SupplementaryUnitTemplateTest','ConfigurationTemplateContractTest'),
                    'only declared supplementary text tests outside monitoring')
            ids,spec,result=('UNITSUP001..005',1553,1555) if stem=='SupplementaryUnitTemplateTest' else ('CONFIGSUP001..004',1556,1557)
            kind='TEST_NOT_JAVA_MAIN'
        require(spec in documents and result in documents,'both spec and result must exist')
        rows.append(dict(**delta,kind=kind,testIdFamily=ids,
          specification=dict(path=str(documents[spec].relative_to(host.ROOT)),sha256=host.sha(documents[spec])),
          result=dict(path=str(documents[result].relative_to(host.ROOT)),sha256=host.sha(documents[result])),
          rd='MON005..013' if delta['owner']=='WBS-P018-09' else 'OPS005/OPS009/SYS002',
          ui='252' if delta['owner']=='WBS-P018-09' else '251/253',
          ss='351 sections6..10' if delta['owner']=='WBS-P018-09' else '343'))
    require(len(rows)==19 and len({r['path'] for r in rows})==19,'all19 unique additions traced')
    class_rows=[]
    prefix='src/schubert-nk-batch/src/main/java/'
    bypath={r['path']:r for r in rows}
    for name,digest in physical['newPhysicalClasses'].items():
        role,entry=name.split(':',1)
        source_path=prefix+entry.removesuffix('.class').split('$',1)[0]+'.java'
        require(role=='batch' and source_path in bypath,'every actual new nested/metadata class has one source owner')
        class_rows.append(dict(className=name,sha256=digest,source=source_path,owner=bypath[source_path]['owner']))
    require(len(class_rows)==16,'all16 actual added physical classes, not inferred from source count')
    value=dict(actualExit=0,source=SOURCE,originalSource=ORIGINAL,
      timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=host.ROOT,text=True).strip(),
      toolSha256=host.sha(Path(__file__)),originalPosts=PINS,sourceRows=rows,physicalRows=class_rows,
      originalExistingClassBytesUnchanged=1669,addedPhysicalClasses=16,
      ordinaryMonitoringRun=dict(source=SOURCE,tests=54,suites=7,counters=component['counters']),
      separateConfigurationRunsNotSummed=True,default485SourceNotReplaced=True,
      testsExecutedByTrace=0,original4222Repeated=False,original44Repeated=False,
      actualVmActions=0,actualDatabaseActions=0,whole451Accepted=False,
      newOriginal190Accepted=0,formalUpdated=False,effortPercent=None)
    os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,sources=len(rows),classes=len(class_rows),testsReplayed=0,
                         manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':
    main()
