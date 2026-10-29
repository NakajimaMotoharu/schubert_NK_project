"""Seven exact public-source ownership references; no target execution or warning suppression."""
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pmd_source_span_ascii import span
from trace_owner_join import canonical
import snapshot_program_qualified_v2 as cfg

SOURCE = cfg.SOURCE
OUT = data.BASE/'PG13944-web-startup-resource-seven-contexts-v1'
MEASURED = ('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
TARGETS = {
    'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebHttpServer.java':('b1e458ef9a9a246f8bb70866dbf671a005bbb569b9c4e27c20b525c20b3180a5','WBS-P018-06',{'mvc':'PMD-07209'}),
    'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebNativeRuntime.java':('c9701244fed7a903c0858a5b8ef4bd78a3ddd499b76bbb9358a5f7181c4bec45','WBS-P018-06',{'currentBroker':'PMD-07255','keys':'PMD-07256','transferRoot':'PMD-07257','assetRoot':'PMD-07258','metricOwner':'PMD-07259','control':'PMD-07260'}),
}
WEB = 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/'
DEPENDENCIES = {
    WEB+'bootstrap/WebApplication.java':'6b8629c49b66679c0514e32df4efc8941b92a36c5757a236054adbc8c176490b',
    WEB+'bootstrap/WebRuntimeExecution.java':'0741f73cae738e645b957acf26d93cfdf21b44b05b655fa8962b55f701d377cb',
    WEB+'bootstrap/WebRuntimeStop.java':'0cedc1417ddc419a11896516ad7e2d76cd6277c42711815120f35191e1cd7a6a',
    WEB+'bootstrap/WebProcessMain.java':'ddb50cf28ae1c73b9cc484c826bc337f3c9d3fe8bdef652e8d0d8d07b05e2c4e',
    WEB+'bootstrap/WebProcessLifetime.java':'e3b00633a7e970eec6770d0ba60a57ef9cf907e4e34340f835b507cf1a1e9414',
    WEB+'messaging/WebBrokerContexts.java':'093e19a0dab933309178946242efbd01c3dc4a47c0f97e1cf0fb1d5807be5c1c',
    WEB+'monitoring/WebServiceMetricBinding.java':'ee7591d71269a4238cdda10c5fbae3c7a61b37b8230f893776329e9d1df7ef64',
    WEB+'bootstrap/WebManagementServer.java':'f4b820069ae18d539f6ceb62fd2b2e3b95afe27dafb0bdaf72e35c1fe53a01cf',
}
DESIGN = {'documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md':'3775cb1faf0b96572f4913d06682100da1861f1d364a66f4118b03e27abf4b82'}
REASONS = {
    'PMD-07209':'mvc aliases result.mvc, an already constructed WebHttpServer final field, not a separately acquired context. The result is captured by the optional native owner before vendor setup/start. Local TWR would close the live context before mappedPaths/HTTP use. SSC312 says an unrefreshed context before Tomcat acquisition is not a started resource. WebHttpServer close keeps stopped/destroyed flags only after vendor return. Complete vendor/MVC disposal and failed-owner retention remain current-whole/runtime pending, not proved here.',
    'PMD-07255':'currentBroker borrows the identical broker field immediately after createRetainingUnknown returns. The field exists before readiness and all later acquisitions, and is closed in the final ordered stop phase. Local alias close would invalidate sender/replies/borrowed contexts during runtime. Factory partial/UNKNOWN cleanup belongs to the retaining factory and outer runtime frame; actual factory/native success is not certified.',
    'PMD-07256':'keys aliases the previously captured codecs owner. Codecs remain live for session/log/revocation services and are closed after transfer roots and before broker. Individual codecs are borrowed, not independently acquired/closed here. A later start failure leaves the field for the runtime close/UNKNOWN path; key material is not read by this audit.',
    'PMD-07257':'transferRoot aliases the transfer field assigned from OwnedTransferDirectory.open before proof/assembly. LargeResultReader borrows this owner through the full HTTP lifetime. Ordered stop closes transfer only after HTTP/workers/metrics/assets and before codecs; local TWR would prematurely release it. Actual FD close/namespace ownership remains pending.',
    'PMD-07258':'assetRoot aliases the assets field, captured before directory proof and MediaRangeService assembly. DescriptorFileResolver borrows it; ordered stop closes it after dependent HTTP/workers/metrics and before transfer. Alias scope is not an independent FD acquisition. No filesystem or actual held directory is opened by the review.',
    'PMD-07259':'metricOwner aliases metrics captured from resource-free prepareContext before initialize. Bindings/HTTP observers/management borrow that context. Partial initialize/start failure retains the same field, and ordered close reaches metrics after HTTP/workers/replies/management. Local close at start return would destroy active observation; actual collector lifetime remains pending.',
    'PMD-07260':'control aliases the management field captured from bind before control.start/promote. The retained runtime, not the alias, owns bound HTTP/executor state; closeWithin uses the original stop budget before metrics/roots/keys/broker release. Binding failure before a returned owner is a factory responsibility. Real listener termination/readiness/Root release is not proven by this reference.',
}
IDS = set(REASONS)

def source_guards(path, text):
    if path.endswith('/WebHttpServer.java'):
        for value in ['private final AnnotationConfigWebApplicationContext mvc;', 'this.mvc = new AnnotationConfigWebApplicationContext();', 'var mvc = result.mvc;', 'if (owner != null) owner.accept(result);', 'tomcat.stop();', 'stopped = true;', 'tomcat.destroy();', 'destroyed = true;']:
            assert value in text
        assert text.index('this.mvc =') < text.index('this.tomcat =')
        assert text.index('if (owner != null) owner.accept(result);') < text.index('tomcat.setBaseDir(') < text.index('tomcat.start();')
        assert text.rindex('tomcat.stop();') < text.rindex('stopped = true;') < text.rindex('tomcat.destroy();') < text.rindex('destroyed = true;')
        assert 'try (mvc)' not in text and 'mvc.close(' not in text
    else:
        pairs = [('currentBroker','broker','broker = WebBrokerContexts.createRetainingUnknown('),('keys','codecs','codecs = WebNativeCodecs.create('),('transferRoot','transfer','transfer ='),('assetRoot','assets','assets ='),('metricOwner','metrics','metrics ='),('control','management','management =')]
        for alias,field,acquired in pairs:
            assert 'var '+alias+' = Objects.requireNonNull('+field+');' in text
            assert text.index(acquired) < text.index('var '+alias+' =')
            assert 'var value = '+field+';' in text
            assert alias+'.close(' not in text and alias+'.closeWithin(' not in text
        assert text.index('var metricOwner =') < text.index('metricOwner.initialize();')
        assert text.index('var control =') < text.index('control.start();') < text.index('control.promote(')
        close = text[text.index('  public void close()'):]
        order = ['http','retry','replay','replies','management','metrics','assets','transfer','codecs','broker']
        offsets = [close.index('var value = '+field+';') for field in order]
        assert offsets == sorted(offsets) and close.count('stop.close(phases);') == 1
        assert 'synchronized (ownerLock)' in close and 'if (stopping.compareAndSet(false, true)) stop.begin();' in close

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
    assert len(result) == 7 and {r['id'] for r in result} == IDS
    return sorted(result,key=lambda r:r['id'])

if __name__ == '__main__':
    invocation = capture(__file__);assert not OUT.exists();result = rows();verify(invocation);OUT.mkdir()
    data.write(OUT/'review.json',dict(source=SOURCE,rows=result,dependencySourceHashes=DEPENDENCIES,approvedDesignHashes=DESIGN))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=7,rawRetained=7,sourceChanged=False,productTestsExecuted=0,coverage=None,nativeQualification=False,newAccepted=0,formalUpdated=False,effortPercent=None,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))
