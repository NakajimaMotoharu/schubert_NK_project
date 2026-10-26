"""Current static small-delta accounting for four already-corrected form tests; no target execution."""
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10910_current_f03_web_metric_delta import attrs

SOURCE = '9c37bc73a20bab2028413db2c08f6bbdf28c76a6'
OUT = data.BASE/'PG11028-current-remaining-form-delta-v1'


def parent_state():
    base_path = data.BASE/'PG10834-current-f03-derived-index-v1/manifest.json'
    base = data.read_checked(base_path,'0ffc85f61a9fefb4b15d4688c980970324fa671c417985d9f7d7abbcb5fe7055')
    rows = data.read_checked(base_path.parent/'current-index.json',base['currentIndexSha256'])
    web_path = data.BASE/'PG10910-current-f03-web-metric-delta-v1/manifest.json'
    web = data.read_checked(web_path,'7c283b56f26f3c73e1b198dee9c91000278b10961713c6de2766c728acf85d66')
    dweb = data.read_checked(web_path.parent/'delta.json',web['deltaSha256'])
    form_path = data.BASE/'PG10968-current-form-delta-v1/manifest.json'
    form = data.read_checked(form_path,'ab7756868701839934166c59efb053380f40467f4c497815385de376357d6e33')
    dform = data.read_checked(form_path.parent/'delta.json',form['deltaSha256'])
    ids = {r['id'] for r in rows}-set(dweb['removedFindingIds'])-set(dform['removedFindingIds'])
    refs = ({r['id'] for r in rows if r['contextReferences']}-set(dweb['removedFindingIds']))
    refs |= {r['id'] for r in dweb['freshRows']}|{r['id'] for r in dweb['legacyContextOverlay']}|{r['id'] for r in dform['mainContextBindings']}
    pending = {r['id'] for r in dweb['legacyContextOverlay']}|{r['id'] for r in dform['mainContextBindings']}|{r['id'] for r in dform['freshRows']}
    assert len(ids) == 9235 and len(refs) == 2724 and len(pending) == 48 and refs <= ids
    return ids,refs,pending


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    ids,refs,pending = parent_state()
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
        '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    original_by_id = {r['id']:r for r in original}
    normal = data.read_checked(data.BASE/'PG11008-form-close-assert-six-compile-v1/manifest.json',
        '5150b4e1aceb6ac51c8a38d253108f6729307cd7df77253b8a37f2c44426ea63')
    previous = data.read_checked(data.BASE/'PG10950-form-literal-six-compile-v1/manifest.json',
        '4cd53877ce16c93b44af747c29afdace410d2dc1ce7fec7eb5ebd48a67093baf')
    current = {p:h for p,h in normal['begin']['inputHashes'].items() if p.startswith('src/') and p.endswith('.java')}
    assert len(current) == 1810 and normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in current.items())
    changed = {p:h for p,h in current.items() if previous['begin']['inputHashes'][p] != h}
    static_path = data.BASE/'PG11012-form-close-assert-static-v1/manifest.json'
    static = data.read_checked(static_path,'d642c529b96c8cac73372108e5ea6423cf829e5ea8923badae39fffe04be5df0')
    assert len(changed) == 4 and changed == static['sourceHashes'] and static['source'] == SOURCE
    context_path = data.BASE/'PG11016-form-remaining-context-v1/manifest.json'
    context = data.read_checked(context_path,'0d166f417ef583245eabbf1ae58702fbc777a9162f41aaf41ae5f22d54246f51')
    contexts = data.read_checked(context_path.parent/'contexts.json',context['contextsSha256'])
    assert context['source'] == SOURCE and context['actualExit'] == 0 and len(contexts) == 12
    cm = {r['id']:r for r in contexts}
    raw = (static_path.parent/'pmd.xml').read_bytes()
    assert data.sha(raw) == static['reports']['pmd']['sha256']
    fresh = []
    for file in ET.fromstring(raw):
        if file.tag.rpartition('}')[2] != 'file':
            continue
        path = str(Path(file.get('name')).relative_to(data.ROOT))
        assert path in changed
        for node in file:
            if node.tag.rpartition('}')[2] != 'violation':
                continue
            matches = [r for r in original if r['path'] == path and r['rule'] == node.get('rule') and
                attrs(r['attributes']) == attrs(node.attrib) and ' '.join(r['message'].split()) == ' '.join((node.text or '').split())]
            assert len(matches) == 1
            old = matches[0]
            assert old['id'] in ids and cm[old['id']]['sourceSha256'] == changed[path] and cm[old['id']]['attributes'] == dict(node.attrib)
            fresh.append(dict(id=old['id'],path=path,source=SOURCE,sourceKind='TEST',rule=node.get('rule'),
                currentInputSha256=changed[path],attributes=dict(node.attrib),originalRowSha256=old['rowSha256'],
                contextManifestSha256='0d166f417ef583245eabbf1ae58702fbc777a9162f41aaf41ae5f22d54246f51',
                status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',oldRuntimeReassigned=False))
    assert len(fresh) == len({r['id'] for r in fresh}) == 12
    scope_ids = {r['id'] for r in original if r['path'] in changed}
    assert len(scope_ids) == 43 and scope_ids <= ids and len(scope_ids&refs) == 8 and not scope_ids&pending
    fresh_ids = {r['id'] for r in fresh}
    removed = scope_ids-fresh_ids
    assert len(removed) == 31 and sum(original_by_id[i]['rule']=='AvoidDuplicateLiterals' for i in removed) == 27
    assert sum(original_by_id[i]['rule']=='CloseResource' for i in removed) == 4 and not removed&refs
    current_ids = ids-removed
    current_refs = (refs-scope_ids)|fresh_ids
    current_pending = (pending-scope_ids)|fresh_ids
    assert len(current_ids) == 9204 and len(current_refs) == 2728 and len(current_pending) == 60
    assert len(current_ids-current_refs) == 6476
    assert sum(original_by_id[i]['sourceKind']=='MAIN' for i in current_ids) == 1512
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'delta.json',dict(source=SOURCE,previousIndexSource=previous['source'],sourceInputDelta=changed,
        replacedSourcePaths=sorted(changed),freshRows=fresh,removedFindingIds=sorted(removed),oldScopeFindings=43,newScopeFindings=12,
        replacedContextWarnings=8,newContextReferencesNet=4,newProductExecutions=0,wholeCurrentAnalyzerReissued=False))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        parentManifestSha256='ab7756868701839934166c59efb053380f40467f4c497815385de376357d6e33',
        deltaSha256=data.sha((OUT/'delta.json').read_bytes()),sourceCount=1810,changedSourcePaths=4,otherSourcePathsUnchanged=1806,
        originalRaw=9409,priorDerivedRaw=9235,sourceDerivedRaw=9204,mainRaw=1512,testRaw=7692,totalPriorCorrections=205,
        sourceScopeCorrectionsAlreadyCounted=31,joinedContextWarnings=2728,sourceReboundCurrentWholePending=60,
        noCurrentReferenceInThisJoin=6476,actualViolationCount=None,productTestsExecuted=0,coverage=None,
        wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
