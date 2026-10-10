"""Same-class diagnostic delta, current sixteen plus qualified selected26; not formal."""
import inspect
import json
import xml.etree.ElementTree as ET
import pg1271_current_native_gap as previous
from pg1271_current_native_gap import W,require,sha,COUNTERS,SOURCE


def coordinates(raw, expected):
    root=ET.fromstring(raw)
    actual={n.attrib['type']:{'missed':int(n.attrib['missed']),'covered':int(n.attrib['covered'])}for n in root.findall('counter')}
    require(all(sum(actual[k].values())==sum(expected[k].values())and actual[k]['missed']<=expected[k]['missed']for k in COUNTERS))
    return previous.coordinates(raw,actual)


def main():
    selected=W/'pg1276-private-export-selected-v1'
    r=json.loads((selected/'manifest.safe.json').read_bytes())
    require(r['actualExit']==0 and r['productionSource']==SOURCE and r['testCounts']=={'tests':26,'failures':0,'errors':0,'skipped':0}and r['staticIssues']==0 and sha(selected/'selected.exec')==r['execSha256'])
    # Explicit allowlist, not a permission derived from the measured result.
    allowed={
      'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/FixedNativeCoverageStopHoldTest.java',
      'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/FixedNativeCoverageRemovalDuringShutdownProbe.java',
      'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/NativeCoverageExportTest.java'}
    require(set(r['changedTestOnly'])==allowed)
    s=inspect.getsource(previous.main)
    old="require(not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml']))"
    require(s.count(old)==1);s=s.replace(old,"require(set(subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml'],text=True).splitlines())==ALLOWED)")
    s=s.replace('pg1271-current-native-gap-v1','pg1277-private-export-counter-v1')
    s=s.replace('require(len(data)==16)',"require(len(data)==16);data.append(SELECTED/'selected.exec')")
    s=s.replace("for module in ('bootstrap','api','batch'):","for module in ('bootstrap',):")
    s=s.replace("'moduleCounters':record['moduleCounters']","'baselineModuleCounters':record['moduleCounters'],'selectedManifestSha256':SELECTED_SHA,'selectedOperatorSource':SELECTED_SOURCE,'selectedTests':26,'totalExecCount':17,'mixedTestRunsDiagnosticOnly':True")
    s=s.replace("'oldNativeImports0':True","'oldNativeImports0':True,'selectedExtraExecCount':1")
    env=dict(previous.__dict__,coordinates=coordinates,ALLOWED=allowed,SELECTED=selected,SELECTED_SHA=sha(selected/'manifest.safe.json'),SELECTED_SOURCE=r['operatorSource'])
    exec(compile(s,'<qualified17 same-byte diagnostic, not formal>', 'exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
