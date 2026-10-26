"""Independent original542 source-span/role binding with ten negative cases; no Product execution."""
from collections import Counter
import copy
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = 'e73e9558971a81d30d7f81f6ab0bc5d9662667d2'
OUT = data.BASE/'PG10830-classloader-context-post-v1'


def contract(rows,original,hashes,roles):
    if len(rows) != 542 or Counter(r['id'] for r in rows) != Counter(original.keys()):
        raise ValueError('all raw542 ids exactly once')
    for row in rows:
        old = original[row['id']]
        if row['path'] != old['path'] or row['coordinates'] != old['attributes'] or row['sourceKind'] != old['sourceKind'] or row['originalRowSha256'] != old['rowSha256']:
            raise ValueError('original raw source coordinates')
        if row['source'] != SOURCE or row['rule'] != 'UseProperClassLoader' or row['sourceSha256'] != hashes[old['path']] or row['sourceSha256'] != old['inputSha256']:
            raise ValueError('exact current input and single vendor premise')
        if row['approvedRole'] != roles[old['module']]['approvedRole'] or row['disposition'] != 'CONTEXT_NOT_APPLICABLE_J2EE_CLASSLOADER_PREMISE':
            raise ValueError('same approved module context')
        if row['qualityGatePass'] is not False or row['foreignContainerSupportProven'] is not False or row['dynamicAuthorizationUnchanged'] is not True:
            raise ValueError('no inferred runtime qualification/authorization')
        if type(row['productTestsExecuted']) is not int or row['productTestsExecuted'] != 0:
            raise ValueError('no invented PT or boolean numeric alias')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    path = data.BASE/'PG10828-classloader-context-v1/manifest.json'
    primary = data.read_checked(path,'38fa14db4463903e7485623a1f4d923eb7b93b25a7236543323474b3b36416db')
    assert primary['source'] == SOURCE and primary['actualExit'] == 0
    assert primary['rawWarningsRemoved'] == primary['productTestsExecuted'] == primary['externalActions'] == 0
    architecture = data.read_checked(data.BASE/'PG10822-global-thread-context-v1/architecture.json',
        '3ebea6b5e82692a68fe91af9552d8dc2206d67395c573ff46028d658cc4b612c')
    ancestor = data.read_checked(data.BASE/'PG10824-global-thread-context-post-v1/manifest.json',
        'a95fcb20299c7c89cfec32c3b13bbc707d2c57792d684c89284c43ed8950fce3')
    assert ancestor['actualExit'] == 0 and ancestor['source'] == architecture['source'] == SOURCE
    hashes = architecture['allCurrentInputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
        '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    selected = [r for r in original if r['rule'] == 'UseProperClassLoader']
    reference = {r['id']:r for r in selected}
    assert len(reference) == len(selected) == 542 and len({r['path'] for r in selected}) == 206
    assert Counter(r['sourceKind'] for r in selected) == Counter(MAIN=1,TEST=541)
    rows = data.read_checked(path.parent/'dispositions.json',primary['dispositionsSha256'])
    contract(rows,reference,hashes,architecture['moduleRoles'])
    for row in rows:
        lines = (data.ROOT/row['path']).read_text().splitlines(keepends=True)
        a = row['coordinates']
        span = ''.join(lines[int(a['beginline'])-1:int(a['endline'])])
        assert data.sha(span.encode()) == row['lineSpanSha256'] and 'getClassLoader(' in span
        if row['sourceKind'] == 'MAIN':
            assert row['id'] == 'PMD-07210' and Path(row['path']).name == 'WebHttpServer.java'
            assert 'context.setParentClassLoader(WebHttpServer.class.getClassLoader());' in span
    assert primary['vendorJarSha256'] == architecture['vendorJarSha256']
    assert 'In J2EE' in primary['vendorDescription'] and 'getContextClassLoader()' in primary['vendorDescription']
    bads = [rows[:-1],rows+[rows[0]]]
    for field,value in [('id','unknown'),('sourceSha256','0'*64),('rule','DoNotUseThreads'),('approvedRole','J2EE_MANAGED'),
        ('dynamicAuthorizationUnchanged',False),('qualityGatePass',True),('productTestsExecuted',1),('productTestsExecuted',False)]:
        bad = copy.deepcopy(rows)
        bad[0][field] = value
        bads.append(bad)
    for bad in bads:
        try: contract(bad,reference,hashes,architecture['moduleRoles'])
        except ValueError: pass
        else: raise AssertionError('wrong scope/stale/alias/invented result accepted')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        primaryManifestSha256=data.sha(path.read_bytes()),rawClassLoaderFindings=542,sourceFiles=206,
        main=1,test=541,allCurrentInputRowsUnchanged=True,originalCoordinatesAndMultiplicityPreserved=True,
        architectureReusedByExactHash=True,metadataNegativeVectors=len(bads),rawWarningsRemoved=0,
        productTestsExecuted=0,coverage=None,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,
        effortPercent=None,dynamicAuthorizationUnchanged=True,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
