"""Independent source and original-ID set verification of the remaining-form current delta."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = '9c37bc73a20bab2028413db2c08f6bbdf28c76a6'
OUT = data.BASE/'PG11030-current-remaining-form-delta-post-v1'


def require(value,message):
    if not value:
        raise ValueError(message)


def contract(delta,fresh,removed,changed):
    require(delta['source'] == SOURCE and delta['sourceInputDelta'] == changed,'exact current source/input delta')
    require(delta['replacedSourcePaths'] == sorted(changed),'exact four source paths')
    require(delta['freshRows'] == fresh and delta['removedFindingIds'] == sorted(removed),'exact current raw rows/original removed IDs')
    require(delta['oldScopeFindings'] == 43 and delta['newScopeFindings'] == 12,'actual old/current XML scope')
    require(delta['replacedContextWarnings'] == 8 and delta['newContextReferencesNet'] == 4,'no duplicate context credit')
    require(delta['newProductExecutions'] == 0 and not delta['wholeCurrentAnalyzerReissued'],'no execution/reanalysis invention')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    path = data.BASE/'PG11028-current-remaining-form-delta-v1/manifest.json'
    primary = data.read_checked(path,'a1b84233e2748889d2e659c3b611d6f8560685f5e7d84edb9a3e2018e9bb6f49')
    delta = data.read_checked(path.parent/'delta.json',primary['deltaSha256'])
    raw = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
        '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    original = {r['id']:r for r in raw}
    def load(folder,digest):
        p = data.BASE/folder/'manifest.json'
        m = data.read_checked(p,digest)
        return m,p.parent
    base,bdir = load('PG10834-current-f03-derived-index-v1','0ffc85f61a9fefb4b15d4688c980970324fa671c417985d9f7d7abbcb5fe7055')
    base_rows = data.read_checked(bdir/'current-index.json',base['currentIndexSha256'])
    web,wdir = load('PG10910-current-f03-web-metric-delta-v1','7c283b56f26f3c73e1b198dee9c91000278b10961713c6de2766c728acf85d66')
    dw = data.read_checked(wdir/'delta.json',web['deltaSha256'])
    form,fdir = load('PG10968-current-form-delta-v1','ab7756868701839934166c59efb053380f40467f4c497815385de376357d6e33')
    df = data.read_checked(fdir/'delta.json',form['deltaSha256'])
    ids = {r['id'] for r in base_rows}-set(dw['removedFindingIds'])-set(df['removedFindingIds'])
    refs = ({r['id'] for r in base_rows if r['contextReferences']}-set(dw['removedFindingIds']))
    refs |= {r['id'] for r in dw['freshRows']}|{r['id'] for r in dw['legacyContextOverlay']}|{r['id'] for r in df['mainContextBindings']}
    pending = {r['id'] for r in dw['legacyContextOverlay']}|{r['id'] for r in df['mainContextBindings']}|{r['id'] for r in df['freshRows']}
    assert (len(ids),len(refs),len(pending)) == (9235,2724,48)
    normal,_ = load('PG11008-form-close-assert-six-compile-v1','5150b4e1aceb6ac51c8a38d253108f6729307cd7df77253b8a37f2c44426ea63')
    old,_ = load('PG10950-form-literal-six-compile-v1','4cd53877ce16c93b44af747c29afdace410d2dc1ce7fec7eb5ebd48a67093baf')
    hashes = normal['begin']['inputHashes']
    changed = {p:h for p,h in hashes.items() if p.startswith('src/') and p.endswith('.java') and old['begin']['inputHashes'][p] != h}
    assert len(changed) == 4 and normal['source'] == SOURCE and normal['actualExit'] == 0
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    static,sdir = load('PG11012-form-close-assert-static-v1','d642c529b96c8cac73372108e5ea6423cf829e5ea8923badae39fffe04be5df0')
    raw_xml = (sdir/'pmd.xml').read_bytes()
    assert data.sha(raw_xml) == static['reports']['pmd']['sha256'] and changed == static['sourceHashes']
    context,cdir = load('PG11016-form-remaining-context-v1','0d166f417ef583245eabbf1ae58702fbc777a9162f41aaf41ae5f22d54246f51')
    contexts = data.read_checked(cdir/'contexts.json',context['contextsSha256'])
    expected = []
    coordinates = {'beginline','endline','begincolumn','endcolumn'}
    for file in ET.fromstring(raw_xml):
        if file.tag.rpartition('}')[2] != 'file':
            continue
        fpath = str(Path(file.get('name')).relative_to(data.ROOT))
        for node in file:
            if node.tag.rpartition('}')[2] != 'violation':
                continue
            attrs = {k:v for k,v in node.attrib.items() if k not in coordinates}
            matches = [r for r in raw if r['path'] == fpath and {k:v for k,v in r['attributes'].items() if k not in coordinates} == attrs
                and ' '.join(r['message'].split()) == ' '.join((node.text or '').split())]
            assert len(matches) == 1
            r = matches[0]
            assert len([c for c in contexts if c['id'] == r['id'] and c['attributes'] == dict(node.attrib) and c['sourceSha256'] == changed[fpath]]) == 1
            expected.append(dict(id=r['id'],path=fpath,source=SOURCE,sourceKind='TEST',rule=node.get('rule'),
                currentInputSha256=changed[fpath],attributes=dict(node.attrib),originalRowSha256=r['rowSha256'],
                contextManifestSha256='0d166f417ef583245eabbf1ae58702fbc777a9162f41aaf41ae5f22d54246f51',
                status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False))
    scope = {r['id'] for r in raw if r['path'] in changed}
    assert len(scope) == 43 and all(original[i]['inputSha256'] == old['begin']['inputHashes'][original[i]['path']] for i in scope)
    fresh_ids = {r['id'] for r in expected}
    assert len(expected) == len(fresh_ids) == 12
    removed = scope-fresh_ids
    contract(delta,expected,removed,changed)
    current_ids = ids-removed
    current_refs = (refs-scope)|fresh_ids
    current_pending = (pending-scope)|fresh_ids
    assert len(removed) == 31 and len(set(original)-current_ids) == 205 and not removed&refs
    assert (len(current_ids),len(current_refs),len(current_pending),len(current_ids-current_refs)) == (9204,2728,60,6476)
    assert sum(original[i]['sourceKind']=='MAIN' for i in current_ids) == 1512
    assert primary['sourceDerivedRaw'] == 9204 and primary['actualViolationCount'] is None and primary['newAccepted'] == 0
    bads = []
    for key,value in [('source','old'),('sourceInputDelta',{}),('freshRows',expected[:-1]),('removedFindingIds',[]),
                      ('newContextReferencesNet',12),('newProductExecutions',40),('wholeCurrentAnalyzerReissued',True)]:
        bad = copy.deepcopy(delta)
        bad[key] = value
        bads.append(bad)
    for bad in bads:
        try:
            contract(bad,expected,removed,changed)
        except ValueError:
            pass
        else:
            raise AssertionError('incomplete/forged raw/source/execution accepted')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=data.sha(path.read_bytes()),
        deltaSha256=primary['deltaSha256'],metadataNegativeVectors=len(bads),sourceDerivedRaw=9204,mainRaw=1512,testRaw=7692,
        referenced=2728,currentWholePending=60,noCurrentReference=6476,totalPriorCorrections=205,
        actualViolationCount=None,productTestsExecuted=0,coverage=None,wholeF03Accepted=False,newAccepted=0,
        oldRuntimeReassigned=False,effortPercent=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
