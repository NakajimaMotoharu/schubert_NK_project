"""78 source-specific consumer/Main reviews; six retry-catch spans deliberately unresolved."""
import inspect
import json
import os
import pg6218_keeper_static_reviews as engine

R='REQUIRED_CONTRACT'
G='AvoidCatchingGenericException'
I='AvoidInstanceofChecksInCatchClause'
E='CompareObjectsWithEquals'
C='CloseResource'
S='AvoidSynchronizedStatement'
EMPTY='EmptyCatchBlock'


def single(queue,positions):
    # Each explicit coordinate belongs to this queue's independently read source, not rule-wide filtering.
    alias,consumer,fatal,kind,rollback,retry,start,notify,rank,selfid,cleanup,cleanrank,cleanid,lock,close,closekind=positions
    return {
        (alias,C):(1,R,f'{queue}: local context aliases the already prepared owner field. It is not a second acquisition; startup failure and normal close retain that field, while listener borrows it for the service lifetime.'),
        (consumer,C):(1,R,f'{queue}: JMSConsumer belongs to the transacted JMSContext and is captured by that context/listener registration. Closing the local consumer on successful start would disable the service. Owner context close/partial startup cleanup, not a local TWR, defines lifetime.'),
        (fatal,G):(1,R,f'{queue}: direct Error and typed failed isolation/unconfirmed rollback are fatal, publish halted before notification, and never enter ordinary retry. This catch distinguishes already committed fatal protocol DLQ from unknown rollback, not a successful exception fallback.'),
        (kind,I):(1,R,f'{queue}: only direct Error needs this extra best-effort context rollback; the typed isolation/rollback failures already carry their protocol transaction state. The type predicate cannot be replaced by a generic successful fallback.'),
        (rollback,EMPTY):(1,R,f'{queue}: failure of best-effort rollback after a fatal signal does not make the transaction successful. halted/terminal was already published, no ACK or normal return receipt is emitted, and the outer owner receives onFatal regardless of rollback failure. Actual Root/native termination is not proven.'),
        (rollback,G):(2,R,f'{queue}: rollback after direct fatal Error may itself throw RTE/Error. Both preserve the already published fatal stop path and prohibit later delivery; swallowing here is isolation, not ordinary retry or successful processing.'),
        (start,G):(2,R,f'{queue}: prepared owner must handle setup/start RTE/Error and clean only its actual acquired context. Native unknown release holds its frame; ordinary component preserves fatal priority and fixed startup failure.'),
        (notify,G):(2,R,f'{queue}: onFatal notification may fail independently of setup. Its RTE/Error must be retained while context cleanup is still attempted; no notification exception can silently turn startup into success.'),
        (rank,I):(4,R,f'{queue}: two exact predicates promote fatal notification only over nonfatal startup. Four actual overlapping PMD spans are retained; direct fatal startup is not replaced by a nonfatal callback failure.'),
        (selfid,E):(1,R,f'{queue}: notification and startup failures are compared by reference to avoid Throwable self-suppression. equals is not an exception-graph identity relation.'),
        (cleanup,G):(2,R,f'{queue}: explicit owned close can throw RTE/Error, with native UNKNOWN retention before this outer path. Ordinary component keeps original/fatal cleanup ranking and never claims the context closed on failure.'),
        (cleanrank,I):(2,R,f'{queue}: cleanup Error is fatal only when retained startup is non-Error; both actual type-test spans represent this required priority. Earlier fatal failure otherwise remains primary.'),
        (cleanid,E):(1,R,f'{queue}: distinct cleanup Throwable is suppressed; identical cleanup/startup object is excluded. This preserves self-suppression safety without a provider-controlled equals call.'),
        (lock,S):(1,R,f'{queue}: private final owner monitor serializes confirmed close cache, with halted published before waiting. It is not this/class or external input; only successful actual context.close sets completion.'),
        (close,G):(2,R,f'{queue}: vendor context close RTE/Error reaches prebuilt native UNKNOWN policy, then ordinary component fatal/redacted failure. closed is not set by the catch, and no downstream native release is inferred.'),
        (closekind,I):(1,R,f'{queue}: actual Error is rethrown directly rather than demoted to the nonfatal fixed close wrapper. Ordinary component keeps the fatal boundary separate from raw diagnostic redaction.')}


SPEC={
 'QuestionWorkConsumers':single('ASYNC FIFO one context',(52,57,71,73,76,81,87,91,92,96,100,101,102,116,120,122)),
 'WebLogConsumers':single('WEB_LOG one context',(63,69,84,87,90,95,101,105,106,110,114,115,116,135,139,141)),
 'SyncRequestConsumers':{
 (71,C):(1,R,'SYNC four contexts: each acquired nonnull context is immediately added to the prepared capacity4 owner list before setup. The returned owner retains all successful acquisitions; partial startup closes only the registered contexts.'),
 (77,C):(1,R,'SYNC consumer belongs to its transacted context and captures that context in the registered callback. Owner contexts, not loop-local TWRs, determine the live four-consumer service lifetime.'),
 (94,G):(1,R,'SYNC direct Error and typed failed isolation/unconfirmed rollback publish halted and one terminal CAS before fatal notification, not the ordinary retry path. Committed fatal protocol DLQ is handled in its separate typed catch.'),
 (97,I):(1,R,'SYNC only a direct Error needs additional best-effort rollback. Typed transaction-isolation failures are already distinguished; no ordinary ACK or successful recovery is inferred from this classification.'),
 (100,EMPTY):(1,R,'SYNC best-effort rollback failure after fatal publication remains halted/terminal; callback still issues onFatal and never ACKs. It is not confirmed rollback or normal processing, and actual owner/native shutdown remains unproven.'),
 (100,G):(2,R,'SYNC direct fatal Error rollback may itself fail with RTE/Error; both retain the prior fatal/UNKNOWN state and stop later deliveries. No provider text is emitted and ordinary retry is not selected.'),
 (111,C):(1,R,'SYNC start loop borrows each registered owned context. Successful startup returns all four to the prepared group; partial failure uses closeAfterFailure and normal owner closes exactly confirmed phases.'),
 (115,G):(2,R,'SYNC any setup/start RTE/Error triggers fatal notification and prepared-group cleanup. There is no successful fallback context; native unknown group release retains the outer frame.'),
 (119,G):(2,R,'SYNC notification RTE/Error is separately retained so failed onFatal cannot skip owned cleanup or silently normalize startup. Fatal notification takes precedence only over nonfatal startup.'),
 (120,I):(4,R,'SYNC two Error predicates implement exact notification/startup fatal priority; all four overlapping raw spans remain. This is required Throwable classification rather than general subtype-driven business logic.'),
 (124,E):(1,R,'SYNC notification != failure prevents self-suppression by actual Throwable reference. Arbitrary equals would not express the Java exception-graph invariant.'),
 (144,S):(1,R,'SYNC private final closeLock protects four per-context successful close flags and final closed. halted is atomically published before the monitor; failed contexts remain unconfirmed while successful ones are not closed twice.'),
 (152,G):(2,R,'SYNC actual context close RTE/Error is accumulated without writing that context success cache. After all ordinary attempts the fixed native UNKNOWN policy runs before any unwind; this catch is not successful cleanup.'),
 (153,I):(1,R,'SYNC Error must supersede an earlier nonfatal context-close failure and be directly propagated after policy. The predicate retains fatal class priority without treating shutdown request as termination.'),
 (155,E):(1,R,'SYNC distinct later close failures may be suppressed on retained failure, but the same Throwable reference cannot be suppressed onto itself.'),
 (172,G):(2,R,'SYNC closeAfterFailure handles the real owned group close boundary RTE/Error, preserving original startup where appropriate and never turning UNKNOWN into successful startup.'),
 (173,I):(1,R,'SYNC cleanup Error over nonfatal startup must escape directly; this actual raw warning belongs to the compound fatal-priority decision, while an existing fatal startup stays primary.'),
 (174,E):(1,R,'SYNC identical startup/cleanup object returns from the helper without self-suppression; the caller still throws startup failure. This return is not normal service completion.')},
 'ApiProcessMain':{
 (87,'DoNotUseThreads'):(1,'CONTEXT_NOT_APPLICABLE','Standalone JavaSE ordinary API installs a handler on its own main thread before startup; no container-owned executor or unrelated thread is modified. Source-only review, not permission to execute the held real Main.'),
 (289,'DoNotUseThreads'):(1,'CONTEXT_NOT_APPLICABLE','Standalone uncaught handler accepts the JVM thread parameter but outputs only fixed API process failed text, never Throwable message/stack/credentials. It neither starts nor stops a thread/process and is not actual Root termination proof.')}
}
CASES={name:('dev.codex.schubert.nk.api.messaging.inbound.ApiNativeRetentionTest',) for name in SPEC}
# ApiProcessMain itself is intentionally unexecuted; no fabricated selected-case refs.


def calculate():
    raw=inspect.getsource(engine.calculate)
    raw=raw.replace("spec={'ServiceProcessResources':CORE,'ApiManagementServer':API,'WebNativeRuntime':WEB}",'spec=SPEC')
    start=raw.index('        testclass=');end=raw.index('        decisions.append',start)
    raw=raw[:start]+"        refs=[] if name=='ApiProcessMain' else [c for c in cases if c['className'].startswith(CASES[name])]\n        if name!='ApiProcessMain' and not refs:raise ValueError('actual original selected component refs')\n"+raw[end:]
    raw=raw.replace('len(decisions)!=44','len(decisions)!=78').replace('all44','all78').replace('reviewed=44','reviewed=78')
    raw=raw.replace('1322 individual','1322 further individual')
    scope={**vars(engine),'PLAN':engine.BASE/'PG6222-jms-static-review-v1/manifest.json',
        'PLAN_SHA':'a3b990c5a7ac30ece51ac84024002f21697afd3874f2b8414f29e3c2f67271b6','SPEC':SPEC,'CASES':CASES}
    exec(compile(raw,'<78 source-specific consumer/Main spans>','exec'),scope)
    rows,value=scope['calculate']()
    value['unresolved'].append('Six ordinary retry catch/empty spans not reviewed: listener preflight is outside rollback try; do not assume confirmed rollback from catch type alone')
    return rows,value


def main():
    rows,value=calculate();os.umask(0o077);out=engine.BASE/'PG6226-consumer-static-review-v1';out.mkdir()
    with (out/'decisions.json').open('x') as f:
        json.dump(rows,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value['decisionsSha256']=engine.sha(out/'decisions.json')
    with (out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,reviewed=78,statusCounts=value['statusCounts'],manifestSha256=engine.sha(out/'manifest.json'))))


if __name__=='__main__':main()
