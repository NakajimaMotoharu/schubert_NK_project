"""Seventeen retained raw JMS type-priority references; public source/XML metadata only."""
from collections import Counter
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pmd_source_span_ascii import span
from trace_owner_join import canonical
import snapshot_program_qualified_v2 as cfg

SOURCE=cfg.SOURCE
OUT=data.BASE/'PG14000-jms-type-priority-seventeen-contexts-v1'
MEASURED=('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
RULE='AvoidInstanceofChecksInCatchClause'
TARGETS=json.loads("{\"src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/config/ApiBrokerContexts.java\":[\"af4602cd8c0906045e5985cba6a4e7e32d43b74e59a060f207705b3166f10330\",\"WBS-P005-03\",[\"PMD-00168\"]],\"src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/config/ArtemisConnectionFactoryProvider.java\":[\"e34f85fb6c359595962afb863089e0f4c874dd78a4108981e1d623ec03b2d6e8\",\"WBS-P005-04\",[\"PMD-00173\",\"PMD-00174\",\"PMD-00175\",\"PMD-00176\"]],\"src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/ArtemisRequestSender.java\":[\"2478a0eb7438a76f10e15719fd9c647c899ec62895fdb8ba7a8e26d72bfc3e6c\",\"WBS-P005-02\",[\"PMD-07355\"]],\"src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxJmsSender.java\":[\"b658f0d221ad087390f22f8445abea835743b2223fa7598d32ccff14a39896d7\",\"WBS-P006-02\",[\"PMD-00305\",\"PMD-00306\"]],\"src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/WebBrokerContexts.java\":[\"093e19a0dab933309178946242efbd01c3dc4a47c0f97e1cf0fb1d5807be5c1c\",\"WBS-P005-02\",[\"PMD-07362\",\"PMD-07363\",\"PMD-07364\",\"PMD-07365\",\"PMD-07370\"]],\"src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebLogDispatcher.java\":[\"76b0c079bbc7704ccf64ee9a42acf88c0f9f4fc8fd461ff5d306d6ff48e11c66\",\"WBS-P006-04\",[\"PMD-07283\",\"PMD-07284\",\"PMD-07289\"]],\"src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebLogMessageSender.java\":[\"8299e7a3b9bef6f654b780dbd06d3831c3a137f806fafdc8e8e480c0473e3738\",\"WBS-P006-04\",[\"PMD-07299\"]]}")
DESIGN={
 'documents/300_SS/320_メッセージング/321_Artemis物理構成・JMS設定設計.md':'2fbf317dcc6d2048abb3c8ecdc9747e7b3d46cdba4753bec6bbc9e3ace5d5d1c',
 'documents/300_SS/320_メッセージング/324_Outbox・Inbox・冪等性・再送設計.md':'2bc99fd66ca1121a1ab4ae44e97aab96b52d4cf4c8145f6a425f89c7b07ce774',
 'documents/300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md':'bf35de0b4d24a253eb75808f0280fa92eb3f02f8ba3a988a227f96c7213781a5',
}
IDS={v for _,_,ids in TARGETS.values() for v in ids}

def reason(path,method):
    name=path.rpartition('/')[2]
    if method=='configureOwned':
        return 'SSC311/315/334: ports precede acquisition, settings are protected by one owned close. Direct secondary Error supersedes only non-Error primary; otherwise retain primary identity and secondary via module attachment. UNKNOWN observer is called before classification; its nonreturn path is not overridden. Suppression-disabled fallback and actual provider cleanup remain dynamically unqualified.'
    if name=='ApiBrokerContexts.java':
        return 'SSC314/334: reverse close attempts cover all unconfirmed factories. Only successful return sets each phase. Select first direct Error over ordinary failure, preserve prior Error and clear private scratch in finally. Observer may retain UNKNOWN without return. Catalog graph fallback is not qualified by this review.'
    if name=='WebBrokerContexts.java':
        return 'SSC311/316/334: stop new contexts under the owner lock. Notify unconfirmed before direct Error propagation; set closed only after confirmed owner close. Nonfatal graph classification precedes fixed redacted catalog; native observer nonreturn and actual close are not proved by this source reference.'
    if name=='OutboxJmsSender.java':
        return 'SSC320: no-primary direct Error is propagated, otherwise wrapped at legacy typed boundary. Direct close Error supersedes only a non-Error primary; an existing primary Error remains. Distinct-secondary guard avoids self-suppression and duplicate typed cause. Owned close runs in finally; graph classification/duplicate/rollback are separate unexecuted dependencies.'
    if name in ('ArtemisRequestSender.java','WebLogMessageSender.java'):
        return 'SSC321: a direct close Error supersedes only a non-Error primary and preserves it as secondary. Existing primary Error keeps identity; other secondary handling uses module-local attachment. No-primary behavior stays at the original boundary. Finally owns one context close; attachment graph, actual JMS, wire wipe and caller outcomes remain dynamically unqualified.'
    if method=='transaction':
        return 'Web manual transaction /1451: rollback Error keeps an already direct primary Error; otherwise rollback Error is promoted. Outer finally still closes the owned connection. This is not the separate direct-close selection rule or actual rollback proof; module attachment graph and database outcomes remain unqualified.'
    assert name=='WebLogDispatcher.java' and method=='closeAfterFailure'
    return 'Web manual transaction /1451: preserve legacy component rule that a distinct direct close Error takes precedence, including over a prior Error; same object is not suppressed into itself. This differs deliberately from SSC320/321 send-close first-primary policy. This review does not apply the sender rule globally, prove actual close or accept all transaction dependencies.'

GUARDS={
 'ArtemisConnectionFactoryProvider.java':[
  'Objects.requireNonNull(onUnconfirmed, "unconfirmed close policy");',
  'if (secondary instanceof Error && !(primary instanceof Error)) {',
  'secondary.addSuppressed(primary);','throw secondary;',
  'TemporaryInfrastructureException.attachSecondary(primary, secondary);','throw primary;'],
 'ApiBrokerContexts.java':[
  'stopping = true;','if (ownerClosed[index]) continue;',
  'ownerClosed[index] = true;',
  'if (failure == null || closing instanceof Error && !(failure instanceof Error))',
  'if (failure != null) onUnconfirmed.accept(failure);','if (failure instanceof Error fatal) throw fatal;',
  'Arrays.fill(closeFailures, null);','stateLock.unlock();'],
 'WebBrokerContexts.java':[
  'if (secondary instanceof Error && !(primary instanceof Error)) {',
  'WebStartupException.attachSecondary(primary, secondary);',
  'stopping = true;','onUnconfirmed.accept(failure);',
  'if (failure instanceof Error fatal) throw fatal;','closed = true;','stateLock.unlock();'],
 'OutboxJmsSender.java':[
  'if (closing instanceof Error fatal) throw fatal;',
  'if (closing instanceof Error fatal && !(primary instanceof Error)) {',
  'fatal.addSuppressed(primary);','throw fatal;',
  '&& !(primary instanceof OutboxSendException typed && closing == typed.getCause()))',
  'primary.addSuppressed(closing);','closeAfterFailure(context, primary);'],
 'ArtemisRequestSender.java':[
  'if (primary == null) {','throw closing;',
  'if (closing instanceof Error fatal && !(primary instanceof Error)) {',
  'fatal.addSuppressed(primary);','WebStartupException.attachSecondary(primary, closing);',
  'closeAfterFailure(context, primary);'],
 'WebLogMessageSender.java':[
  'if (primary == null) throw closing;',
  'if (closing instanceof Error fatal && !(primary instanceof Error)) {',
  'fatal.addSuppressed(primary);','WebStartupException.attachSecondary(primary, closing);',
  'closeAfterFailure(context, primary);','Arrays.fill(wire, (byte) 0);'],
 'WebLogDispatcher.java':[
  'catch (SQLException | RuntimeException | Error failure)',
  'if (failure instanceof Error) {','WebStartupException.attachSecondary(failure, fatal);',
  'throw failure;','closeAfterFailure(connection, primary);',
  'if (closing instanceof Error fatal && fatal != primary) {',
  'WebStartupException.attachSecondary(primary, closing);'],
}

def source_guards(path,text):
    for phrase in GUARDS[path.rpartition('/')[2]]:assert phrase in text
    if path.endswith('ArtemisConnectionFactoryProvider.java') or path.endswith('WebBrokerContexts.java'):
        begin=text.index('  static ActiveMQConnectionFactory configureOwned(')
        code=text[begin:]
        assert code.index('Objects.requireNonNull(acquire,') < code.index('var factory =') < code.index('factory.setCallTimeout(') < code.index('factory.close();') < code.index('onUnconfirmed.accept(secondary);') < code.index('if (secondary instanceof Error')
    if path.endswith('ApiBrokerContexts.java'):
        body=text[text.index('  public void close()'):]
        assert body.index('owners.get(index).close();')<body.index('ownerClosed[index] = true;')<body.index('closed = true;')
    if path.endswith('WebBrokerContexts.java'):
        body=text[text.index('  public void close()'):]
        assert body.index('owner.close();')<body.index('onUnconfirmed.accept(failure);')<body.index('closed = true;')

def wire(value):return json.dumps(value,sort_keys=True,separators=(',',':'))

def rows():
    normal,_=cfg.normal();hashes=normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    for p,pin in DESIGN.items():assert data.sha(subprocess.check_output(['git','show','origin/main:'+p],cwd=data.ROOT))==data.sha((data.ROOT/p).read_bytes())==pin
    measured=data.read_checked(data.BASE/MEASURED[0]/'manifest.json',MEASURED[1])
    assert measured['actualExit']==0 and measured['analysisComplete'] and not measured['processingErrors']
    facts=data.read_checked(data.BASE/MEASURED[0]/'findings.json',measured['findingsSha256'])
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    result=[]
    for path,(pin,owner,identities) in TARGETS.items():
        text=(data.ROOT/path).read_text();assert data.sha(text.encode())==hashes[path]==pin;source_guards(path,text)
        ownership=canonical(path,logical);assert ownership['canonicalOwner']==ownership['canonicalCostOwner']==owner
        selected=[r for r in facts if r['path']==path and r['rule']==RULE]
        prior=[r for r in original if r['id'] in identities]
        assert len(selected)==len(prior)==len(identities) and Counter(wire(r['attributes']) for r in selected)==Counter(wire(r['attributes']) for r in prior)
        seen=Counter()
        for row in sorted(prior,key=lambda r:r['id']):
            attributes=row['attributes'];key=wire(attributes);matches=[v for v in selected if v['attributes']==attributes]
            assert all(v['sourceSha256']==pin for v in matches) and row['inputSha256']==pin
            start,end,value=span(text,attributes);assert value=='Error'
            anchor=text.rfind('catch (',0,start);assert anchor>=0
            result.append(dict(id=row['id'],path=path,source=SOURCE,sourceSha256=pin,rule=RULE,attributes=attributes,originalRowSha256=row['rowSha256'],spanStart=start,spanEndExclusive=end,spanSha256=data.sha(value.encode()),typeToken=value,catchAnchor=anchor,occurrenceOrdinal=seen[key],rawDiagnosticMultiplicity=len(matches),reason=reason(path,attributes['method']),disposition='TYPE_PRIORITY_CONTRACT_CURRENT_WHOLE_JOIN_PENDING',rawRetained=True,currentWholeJoinPending=True,sourceChanged=False,productTestsExecuted=0,nativeRuntimeProven=False,**ownership))
            seen[key]+=1
        assert all(seen[k]==len([v for v in selected if wire(v['attributes'])==k]) for k in seen)
    assert len(result)==17 and {r['id'] for r in result}==IDS
    assert len({(r['path'],r['spanStart'],r['spanEndExclusive']) for r in result})==12
    assert len({(r['path'],r['catchAnchor']) for r in result})==9
    return sorted(result,key=lambda r:r['id'])

if __name__=='__main__':
    invocation=capture(__file__);assert not OUT.exists();result=rows();verify(invocation);OUT.mkdir()
    data.write(OUT/'review.json',dict(source=SOURCE,rows=result,approvedDesignHashes=DESIGN,legacyWebTransactionReview='evidence/01_PT/018_NK-OPS-001/1451_Web手動transaction_secondary保持・rollback単体テスト仕様.md'))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewSha256=data.sha((OUT/'review.json').read_bytes()),sourceContexts=17,uniqueOperandSpans=12,uniqueCatchClauses=9,rawRetained=17,sourceChanged=False,productTestsExecuted=0,coverage=None,nativeQualification=False,newAccepted=0,formalUpdated=False,effortPercent=None,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))
