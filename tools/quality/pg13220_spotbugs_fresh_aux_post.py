"""Independent six XML class inventories, source/aux provenance and old18-to-current0 resolution proof."""
import copy
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG13220-spotbugs-fresh-aux-post-v1'

def validate(value,reference):
    assert value == reference
    assert value['totalPhysicalMain'] == 1843 and value['missingClasses'] == value['analysisErrors'] == value['bugs'] == 0
    assert value['productTestsExecuted'] == value['newAccepted'] == 0 and not value['wholeF03Accepted']

def main():
    invocation = capture(__file__);assert not OUT.exists()
    plan = data.read_checked(data.BASE/'PG13218-spotbugs-fresh-aux-plan-recovery-v1/manifest.json','a60a6ff0579588e9a10b5a2de6b2d2f4587f983408645a87e8cd4c7ad6917564')
    result = data.read_checked(data.BASE/'PG13216-spotbugs-fresh-six-cli-v1/manifest.json','3ec8326e0c54daf26b3bc500a7b2ceb62f34abc0a9647c8ed140e9f19708f8c0')
    proof = data.read_checked(data.BASE/'PG13212-resource-db-literal-v1/manifest.json','f0a0817f4a3cbac3d4ebacc267e892b09510c9994cf31daf6c3e1e20821f3a65')
    assert plan['source'] == result['source'] == proof['source'] == '6d7f55c22a3ffec8a9013e706282ac845c595492'
    assert result['actualExit'] == result['spotbugsSixExit'] == proof['actualExit'] == 0 and proof['allMainPhysicalUnchanged'] == 1843
    hashes = {**plan['toolRuntimeHashes'],**plan['auxiliaryClasspathHashes'],**plan['currentJarHashes']}
    assert all(data.sha(Path(p).read_bytes()) == sha for p,sha in hashes.items())
    stages = result['stages'];assert len(stages) == 6 and all(x['actualExit'] == 0 and not x['timedOut'] for x in stages)
    rows = {};resolved = []
    for role,jar in plan['currentJarsByRole'].items():
        raw = (data.BASE/'PG13216-spotbugs-fresh-six-cli-v1'/(role+'.xml')).read_bytes();assert data.sha(raw) == result['reports'][role]['sha256']
        root = ET.fromstring(raw);assert root.get('version') == '4.10.4'
        assert root.find('Project').findall('Jar')[0].text == jar and len(root.find('Project').findall('Jar')) == 1
        aux = [x.text for x in root.find('Project').findall('AuxClasspathEntry')]
        assert len(aux) == len(set(aux)) and set(aux) == set(plan['auxiliaryClasspathHashes'])
        assert not [x for x in root.iter() if x.tag in ['BugInstance','MissingClass','Error']]
        with zipfile.ZipFile(jar) as archive:physical = {x[:-6].replace('/','.') for x in archive.namelist() if x.endswith('.class')}
        stats = [x.get('class') for x in root.iter('ClassStats')]
        assert len(stats) == len(set(stats)) and set(stats) == physical and int(root.find('FindBugsSummary').get('total_classes')) == len(physical)
        rows[role] = dict(physicalClasses=len(physical),reportedClasses=len(stats),reportSha256=data.sha(raw),jarSha256=plan['currentJarHashes'][jar],exactClassSet=True,missingClasses=0,analysisErrors=0,bugs=0)
        stale = set()
        for item in plan['oldAux'][role]['staleProjectJars']:
            assert data.sha(Path(item['path']).read_bytes()) == item['sha256']
            with zipfile.ZipFile(item['path']) as archive:stale.update(archive.namelist())
        for name in plan['oldMissingClasses'][role]:
            entry = name.replace('.','/')+'.class';owners = [owner for owner,classes in plan['expectedClasses'].items() if entry in classes]
            assert len(owners) == 1 and entry not in stale
            resolved.append(dict(module=role,className=name,owner=owners[0],oldStaleProjectAuxContained=False,freshSourceContains=True,currentMissing=False))
    assert len(resolved) == 18 and len({r['className'] for r in resolved}) == 8
    reference = dict(source=result['source'],rows=rows,oldToCurrentResolution=resolved,totalPhysicalMain=sum(r['physicalClasses'] for r in rows.values()),
        oldMissingOccurrences=18,currentMissingOccurrences=0,missingClasses=0,analysisErrors=0,bugs=0,sameToolVersion='4.10.4',effort='max',threshold='low',exclusionFiltersAdded=False,
        oldResultRewritten=False,productTestsExecuted=0,coverage=None,newAccepted=0,wholeF03Accepted=False,whole451Accepted=False)
    validate(reference,reference);negatives = []
    for label,change in [('source',lambda x:x.update(source='0'*40)),('class-count',lambda x:x.update(totalPhysicalMain=1643)),('missing',lambda x:x.update(missingClasses=1)),
        ('analysis-error',lambda x:x.update(analysisErrors=1)),('scope',lambda x:x['rows']['api'].update(physicalClasses=1)),('old-rewrite',lambda x:x.update(oldResultRewritten=True)),
        ('PT',lambda x:x.update(productTestsExecuted=1843)),('accepted',lambda x:x.update(newAccepted=1))]:
        bad = copy.deepcopy(reference);change(bad);assert json.dumps(bad,sort_keys=True) != json.dumps(reference,sort_keys=True)
        try:validate(bad,reference)
        except AssertionError:negatives.append(label)
        else:raise AssertionError('incomplete static result accepted')
    verify(invocation);OUT.mkdir();data.write(OUT/'verification.json',reference)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=result['source'],invocation=invocation,verificationSha256=data.sha((OUT/'verification.json').read_bytes()),
        metadataNegativeVectors=len(negatives),nonVacuousLabels=negatives,fullPhysicalMain=1843,resolvedOldMissingOccurrences=18,currentMissingClasses=0,currentAnalysisErrors=0,currentBugs=0,
        originalIncompleteReportsPreserved=True,analysisReexecuted=False,productTestsExecuted=0,newAccepted=0,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
