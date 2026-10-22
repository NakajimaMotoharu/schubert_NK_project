"""Independently qualify the completed two expected contract failures; no rerun."""
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pg6966_chr_adapter_host as host


def main():
    slot = host.W/'pg6972-chr-path-red-v1'
    begin = json.loads((slot/'begin.safe.json').read_bytes())
    result = json.loads((slot/'manifest.safe.json').read_bytes())
    host.require(result['actualExit'] == 1 and result['beginSha256'] == host.sha(slot/'begin.safe.json')
                 and result['originalBaselineUnchanged'] and result['snapshotInputsUnchanged'], 'original genuine failed terminal and immutable input')
    snapshot = slot/'snapshot'
    host.require(all(host.sha(snapshot/p) == h for p,h in begin['inputHashes'].items()), 'actual complete original input bytes')
    rows,xmls = [],{}
    for path in sorted((snapshot/'program/characterization/target/surefire-reports').glob('TEST-*.xml')):
        xmls[path.name] = host.sha(path)
        root = ET.parse(path).getroot()
        for case in root.findall('testcase'):
            rejected = case.find('failure')
            host.require(case.find('error') is None and case.find('skipped') is None
                         and not any('flaky' in n.tag.lower() or 'rerun' in n.tag.lower() for n in case), 'no error/skipped/flaky/rerun normalized')
            row = dict(clazz=case.get('classname'),method=case.get('name'),xmlSha256=host.sha(path),
                       result='FAIL' if rejected is not None else 'PASS')
            if rejected is not None:
                text = ''.join(rejected.itertext())
                host.require('IllegalArgumentException' in text and 'NullPointerException' in text,
                             'exact independent expected contract vs actual NPE, not another setup failure')
                row.update(expectedException='java.lang.IllegalArgumentException',actualException='java.lang.NullPointerException',
                           failureBodySha256=hashlib.sha256(text.encode()).hexdigest())
            rows.append(row)
    failures = {r['method'] for r in rows if r['result'] == 'FAIL'}
    host.require(len(rows) == 43 and len(xmls) == 5 and failures == {
        'preflightRejectsParentlessLogPathWithoutNpe','jsonWriterRejectsParentlessOutputWithoutNpe'}, 'original41 passed, new two fail only')
    host.require(not (snapshot/'null.part').exists(), 'no relative temporary residual in owned snapshot')
    value = dict(actualExit=0,source=begin['source'],underlyingMavenExit=1,tests=43,suites=5,
                 passedOriginal=41,failedNew=2,expectedRedOnly=True,errors=0,skipped=0,flaky=0,
                 failureNames=sorted(failures),cases=rows,sourceInputs=begin['inputHashes'],
                 originalBeginSha256=host.sha(slot/'begin.safe.json'),originalExitSha256=host.sha(slot/'exit.safe.json'),
                 originalManifestSha256=host.sha(slot/'manifest.safe.json'),originalBaselineUnchanged=True,
                 nullPartResidual=False,newAcceptance=0,formalUpdated=False,toolSha256=host.sha(Path(__file__)))
    out = host.BASE/'PG6974-chr-path-red-original-v1';out.mkdir();host.write(out/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,underlyingMavenExit=1,passedOriginal=41,failedNew=2,manifestSha256=host.sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
