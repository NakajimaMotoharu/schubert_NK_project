"""Nine exact public-source ownership references; no target execution or warning suppression."""
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pmd_source_span_ascii import span
from trace_owner_join import canonical
import snapshot_program_qualified_v2 as cfg

SOURCE = cfg.SOURCE
OUT = data.BASE/'PG13976-last-main-resource-nine-contracts-v1'
MEASURED = ('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
TARGETS = {
    'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MaintenanceRunFiles.java':('5518c763e1ee78863d9071106b14f15e875b86ad7feac5bf504ffa446e22dc82','WBS-P004-03',{'current':'PMD-02845','parent':'PMD-02846','root':'PMD-02856'}),
    'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/RootFailedStartRecovery.java':('5018386f09b4e29ed51e94c1784bd87f257f80fdbd78257eac305d600c7efa04','WBS-P017-12',{'marker':'PMD-02918'}),
    'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/BackupUnitStartClient.java':('505591e7159e2e8d8cb86ffab1e7395ca9d7cdd9e4c796f14d66064a54cd600c','WBS-P017-06',{'marker':'PMD-03027','stdout':'PMD-03044','stderr':'PMD-03045'}),
    'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/MaintenanceUnitStopClient.java':('ae53eb1a23d05cadb270554222d74c84d64a29adedab5666f15b2e20135470c2','WBS-P018-04',{'stdout':'PMD-03102','stderr':'PMD-03103'}),
}
DEPENDENCIES = {
    'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/BackupStartIntentFiles.java':'2c0eb6e6b079ce54c0368655d2f854e946e5390c72a3f02e71a2b420660b3d11',
    'src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/ResourceScope.java':'639d3e7a51ad7d4fd2b45a9d5b8f7536ece257f08b0db9955249704009d00bbf',
}
DESIGN = {
    'documents/300_SS/340_batch・基盤/341_朝batch・backup・削除・再実行設計.md':'b721e6f7d0ee3f17cfe1a2d38512623814b0a10c8a7ad8ae737c62eeda192195',
    'documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md':'d8be70ce4c170df7939f7803723bb021c99ba40a72819f9b5d861731425332b2',
}
REASONS = {
    'PMD-02845':'current borrows the indexed private verification view. The first root and each child are acquired by enclosing ResourceScope callbacks; the recursive list preserves ancestors for later identity checks. Local current.close would prematurely release a still-needed ancestor. Private directory verification and real descriptors are not executed here.',
    'PMD-02846':'parent is either current or views[3] for the sibling attempts lookup while runs remains held. It is a borrowed ancestor, not newly acquired. Only the child returned by openExistingChild is a new owner and has ResourceScope close. The enclosing verification root scope releases parents after recursion; local alias close would duplicate that ownership.',
    'PMD-02856':'read.root borrows Session.roots[rootIndex], captured by nested root acquisition scopes before Session construction. The session is invalidated on every callback exit, and record reads reuse the same root for pre/post namespace/whole-graph checks. Only returned byte copies are locally owned and cleared in finally. No root or private file is opened by this source audit.',
    'PMD-02918':'marker is a metadata view from an existing markers list; each package constructor merely stores the same caller-owned root. No extra descriptor is acquired by constructing these views. BackupStartIntentFiles.close would close that shared root, so a local loop TWR would release the borrowed outer owner before the pair/quarantine gates finish. Real pair retirement, restoration and actual root release remain HOLD/unproven.',
    'PMD-03027':'beginNative receives an owned marker from the native factory and transfers marker plus exact token into the returned MarkerLease closure. A successful retire calls marker.retire before marker.close; begin failure attempts close and rethrows, never returns an acquired lease. Local TWR would close the marker before external start/parent proof. Retire/close exception precedence and actual native closure remain unqualified; no real marker is created by this audit.',
    'PMD-03044':'startup stdout is captured only after the retained process has terminated within the same budget. Failure acquiring stderr attempts stdout close; otherwise closeBoth attempts stdout and stderr even when the first fails. Failed close returns UNKNOWN before a client status is published; streamsClosed is an attempted-pair flag, not successful Unit/lock release proof.',
    'PMD-03045':'startup stderr is acquired inside the guarded stdout ownership path, then passed to closeBoth. Its close is attempted even after stdout failure because closeOne(stderr) is evaluated before clean. Any close failure leaves UNKNOWN/poisoned or attempted flags and cannot retire/unlock. No real systemctl process or stream is opened here.',
    'PMD-03102':'stop-client stdout follows the same retained-process ownership, guarded stderr acquisition and closeBoth route. UNKNOWN on close/wait/interruption failure is not a stop success or resource-release certificate. The exact client operation remains unexecuted in this static reference.',
    'PMD-03103':'stop-client stderr is a separately captured stream included in closeBoth after stdout, with unconditional attempt despite earlier failure. Only both closes plus context recheck allow a known client exit status, which still is not whole-Unit terminal proof. No retry of an uncertain descriptor, actual stop, or Root operation is performed.',
}
IDS = set(REASONS)

def source_guards(path, text):
    if path.endswith('/MaintenanceRunFiles.java'):
        assert 'var current = views.get(index);' in text
        assert 'var parent = index == 4 ? views.get(3) : current;' in text
        assert 'OwnedTransferDirectory root = roots.get(rootIndex);' in text
        assert 'this.roots = List.copyOf(roots);' in text and 'session.invalidate();' in text
        assert '() -> parent.openExistingChild(names[index]),' in text
        assert 'return verifyStartupPrivate(List.copyOf(added), index + 1);' in text
        begin = text.index('    private Boolean verifyStartupPrivate(');end = text.index('    public MaintenanceCompletion complete(',begin)
        body = text[begin:end];assert 'current.close(' not in body and 'parent.close(' not in body
        begin = text.index('    private <T> T read(');end = text.index('    private void verifyNamespace(',begin)
        body = text[begin:end];assert 'root.close(' not in body
        assert 'captured.add(new CapturedFile(root, name, original));' in body and 'Arrays.fill(bytes, (byte) 0);' in body
    elif path.endswith('/RootFailedStartRecovery.java'):
        begin = text.index('  static void retirePair(');end = text.index('  public static void quarantinePair(',begin)
        body = text[begin:end]
        assert '.map(name -> new BackupStartIntentFiles(root, security, io, gate, name))' in body
        assert 'for (var marker : markers) intents.add(marker.observeQuarantine());' in body
        assert 'marker.close(' not in body and 'root.close(' not in body
        assert 'markers.get(index).retire(intents.get(index));' in body and 'quarantinePair(root, security, io, expected);' in body
    else:
        assert path.endswith('/BackupUnitStartClient.java') or path.endswith('/MaintenanceUnitStopClient.java')
        if path.endswith('/BackupUnitStartClient.java'):
            begin = text.index('  private static MarkerLease beginNative(');end = text.index('  static BackupUnitStartClient create(',begin);body = text[begin:end]
            assert 'var marker = BackupStartIntentFiles.create(root, expected, target);' in body
            assert body.index('var token = marker.begin();') < body.index('return () -> {') < body.index('marker.retire(token);') < body.index('marker.close();')
            assert body.count('marker.close();') == 2 and 'throw failure;' in body
        body = text[text.index('    public Status awaitClient()'):]
        assert 'var stdout = Objects.requireNonNull(process.getInputStream(),' in body
        assert 'stderr = Objects.requireNonNull(process.getErrorStream(),' in body
        assert 'closeOne(stdout);' in body and 'throw failure;' in body
        assert body.index('boolean closed = closeBoth(stdout, stderr);') < body.index('streamsClosed = true;') < body.index('if (!closed) return Status.UNKNOWN;') < body.index('retainedStatus =')
        assert 'boolean clean = closeOne(stdout);' in body and 'return closeOne(stderr) && clean;' in body
        assert 'poisoned = true;' in body and 'stream.close();' in body

def rows():
    normal,_ = cfg.normal();hashes = normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in hashes.items())
    for p,pin in DEPENDENCIES.items():assert data.sha((data.ROOT/p).read_bytes()) == hashes[p] == pin
    for p,pin in DESIGN.items():
        public = subprocess.check_output(['git','show','origin/main:'+p],cwd=data.ROOT)
        assert data.sha(public) == data.sha((data.ROOT/p).read_bytes()) == pin
    measured = data.read_checked(data.BASE/MEASURED[0]/'manifest.json',MEASURED[1]);assert measured['actualExit'] == 0 and measured['analysisComplete'] and not measured['processingErrors']
    facts = data.read_checked(data.BASE/MEASURED[0]/'findings.json',measured['findingsSha256'])
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    logical = {r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    result = []
    for path,(pin,owner,fields) in TARGETS.items():
        text = (data.ROOT/path).read_text();assert data.sha(text.encode()) == hashes[path] == pin;source_guards(path,text)
        ownership = canonical(path,logical);assert ownership['canonicalOwner'] == ownership['canonicalCostOwner'] == owner
        selected = [r for r in facts if r['path'] == path and r['rule'] == 'CloseResource'];assert len(selected) == len(fields)
        for row in selected:
            attributes = row['attributes'];variable = attributes['variable'];identity = fields[variable];old, = [r for r in original if r['id'] == identity]
            assert old['path'] == path and old['rule'] == row['rule'] and old['attributes'] == attributes and old['inputSha256'] == row['sourceSha256'] == pin
            start,end,value = span(text,attributes);assert value == variable
            result.append(dict(id=identity,path=path,source=SOURCE,sourceSha256=pin,rule=row['rule'],variable=variable,attributes=attributes,originalRowSha256=old['rowSha256'],spanStart=start,spanEndExclusive=end,spanSha256=data.sha(value.encode()),reason=REASONS[identity],disposition='OWNERSHIP_CONTRACT_CURRENT_WHOLE_JOIN_PENDING',rawRetained=True,currentWholeJoinPending=True,sourceChanged=False,productTestsExecuted=0,nativeRuntimeProven=False,**ownership))
    assert len(result) == 9 and {r['id'] for r in result} == IDS
    return sorted(result,key=lambda r:r['id'])

if __name__ == '__main__':
    invocation = capture(__file__);assert not OUT.exists();result = rows();verify(invocation);OUT.mkdir()
    data.write(OUT/'review.json',dict(source=SOURCE,rows=result,dependencySourceHashes=DEPENDENCIES,approvedDesignHashes=DESIGN))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=9,rawRetained=9,sourceChanged=False,productTestsExecuted=0,coverage=None,nativeQualification=False,newAccepted=0,formalUpdated=False,effortPercent=None,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))
