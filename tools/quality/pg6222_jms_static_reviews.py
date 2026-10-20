"""56 explicit current JMS ownership/exception applicability sites; no new PT or native claim."""
import inspect
import json
import os
import pg6218_keeper_static_reviews as prior

SPEC={
 'ArtemisConnectionFactoryProvider':{
 (96,'AvoidCatchingGenericException'):(2,'REQUIRED_CONTRACT','All twelve locator settings are inside the single acquired factory protection region. Configuration RTE/Error must close that unreturned factory; normal configured factory ownership is returned, not closed early.'),
 (99,'AvoidCatchingGenericException'):(2,'REQUIRED_CONTRACT','Secondary factory-close RTE/Error is delivered to the prebuilt native UNKNOWN policy before ordinary component exception ranking. Catching only JMS checked exceptions would miss this vendor unchecked release boundary.'),
 (101,'AvoidInstanceofChecksInCatchClause'):(4,'REQUIRED_CONTRACT','Two exact Error predicates promote fatal cleanup over nonfatal setup, otherwise preserve original fatal setup. Four overlapping PMD spans are retained; independent compound factory cases, not rule suppression, support this boundary.'),
 (105,'CompareObjectsWithEquals'):(1,'REQUIRED_CONTRACT','Throwable reference identity prevents primary.addSuppressed(primary). Structural/value equality is not the self-suppression relation; distinct failures retain the original component exception order.')},
 'ApiBrokerContexts':{
 (104,'CloseResource'):(1,'REQUIRED_CONTRACT','sync is the first returned prepared-owner factory. It is immediately registered in preallocated owners capacity3, before later factory acquisition. The returned owner keeps it live; local TWR would prematurely stop the live broker.'),
 (110,'CloseResource'):(1,'REQUIRED_CONTRACT','webLog is the second returned factory, immediately registered under the already prepared owner. A later factory failure closes registered owners in reverse; the provider owns its own unreturned failed factory.'),
 (115,'CloseResource'):(1,'REQUIRED_CONTRACT','async is the third returned factory. All three registered factories transfer to final retained fields with no further provider call; owner close handles each actual successful phase. No speculative close of unacquired factories occurs.'),
 (123,'AvoidCatchingGenericException'):(2,'REQUIRED_CONTRACT','Partial broker constructor startup must reclaim only already returned factories on RTE/Error. Native unconfirmed close retains UNKNOWN; ordinary component keeps its specified primary with reverse secondaries, not an invented fatal-priority change.'),
 (127,'AvoidCatchingGenericException'):(2,'REQUIRED_CONTRACT','AutoCloseable factory owner may throw checked Exception or Error. Each partial reverse close uses native UNKNOWN before continuing; ordinary component records secondaries against original startup failure. Provider-local failed acquisition is not closed again.'),
 (130,'CompareObjectsWithEquals'):(1,'REQUIRED_CONTRACT','Only a distinct cleanup Throwable is suppressed on constructor primary. Reference identity is mandatory for Java self-suppression safety; equals cannot substitute.'),
 (198,'AvoidCatchingGenericException'):(1,'REQUIRED_CONTRACT','Credential supplier RuntimeException/null is rejected as fixed unavailable without provider diagnostic or password graph. It is failure, never successful authentication; Error is not caught here. Stop state excludes new contexts before copying.'),
 (207,'AvoidCatchingGenericException'):(1,'REQUIRED_CONTRACT','Context creation RuntimeException/null and invalid credential length become fixed unavailable. The owned char copy is wiped in finally even when a fatal Error propagates; successful context ownership is returned to consumer, not locally closed.'),
 (229,'AvoidCatchingGenericException'):(2,'REQUIRED_CONTRACT','Actual registered AutoCloseable owners are attempted in reverse, with success cache only after each close returns. Exception/Error are accumulated for explicit failure/native hold; no unconfirmed phase is marked closed.'),
 (230,'AvoidInstanceofChecksInCatchClause'):(1,'REQUIRED_CONTRACT','Direct Error must dominate an earlier nonfatal owner-close failure. The final Error is rethrown directly after the UNKNOWN policy; equality/type erasure would lose this fatal classification.')},
 'WebBrokerContexts':{
 (63,'CloseResource'):(1,'REQUIRED_CONTRACT','configured is returned only after supplier-local settings protection, and is immediately captured as both factory and owner in the already prepared instance. Native policy/lock/password fields exist before acquisition. No local TWR may stop the returned live broker.'),
 (118,'AvoidCatchingGenericException'):(2,'REQUIRED_CONTRACT','RTE/Error from any of the twelve fixed settings requires one close of the unreturned owned factory; successful configuration returns ownership. This is the same protected resource boundary, not generic validation recovery.'),
 (121,'AvoidCatchingGenericException'):(2,'REQUIRED_CONTRACT','Vendor unchecked cleanup failure first enters fixed native UNKNOWN policy. Finite ordinary component then uses explicit Error/primary ranking and self-suppression guard; unconfirmed native cleanup cannot unwind downstream owners.'),
 (123,'AvoidInstanceofChecksInCatchClause'):(4,'REQUIRED_CONTRACT','Two predicates preserve fatal setup unless fatal cleanup supersedes nonfatal setup. The four actual overlapping warning spans are individually retained, not removed by a rule-wide exemption.'),
 (127,'CompareObjectsWithEquals'):(1,'REQUIRED_CONTRACT','Reference inequality excludes suppressing a Throwable onto itself while retaining distinct ordinary cleanup failure. It is identity, not a domain value comparison.'),
 (160,'AvoidCatchingGenericException'):(1,'REQUIRED_CONTRACT','Credential supplier RuntimeException/null is a fixed unavailable failure under stateLock; Error still propagates. No raw supplier text, credential or successful fallback context is produced.'),
 (169,'AvoidCatchingGenericException'):(1,'REQUIRED_CONTRACT','Invalid credential/context creation RTE/null becomes fixed unavailable and the local char copy is always wiped. Returned real JMSContext ownership belongs to the consumer, not this borrowed factory callback.'),
 (187,'AvoidCatchingGenericException'):(2,'REQUIRED_CONTRACT','AutoCloseable owner may fail with checked or unchecked exception/Error. Native UNKNOWN policy precedes any unwind, ordinary failure traverses fatal graph before redacted fixed exception. closed cache is written only on confirmed normal close.'),
 (189,'AvoidInstanceofChecksInCatchClause'):(1,'REQUIRED_CONTRACT','Direct Error must be rethrown without an IllegalStateException wrapper; indirect fatal graphs are separately checked by SessionStoreException.preserveFatal. This type test is the declared fatal boundary.')},
 'ApiMessagingRuntime':{
 (183,'AvoidCatchingGenericException'):(2,'REQUIRED_CONTRACT','Startup of the prepared list of sync/WebLog/optional async groups must send fatal notification and close already opened groups on RTE/Error. All fixed ownership state/list capacity exists before first group acquisition.'),
 (187,'AvoidCatchingGenericException'):(2,'REQUIRED_CONTRACT','Notification callback itself may fail with RTE/Error; retaining its priority while still closing prepared groups requires this exact catch. Native group unknown hold remains inside release, so normal parent return is not inferred.'),
 (188,'AvoidInstanceofChecksInCatchClause'):(4,'REQUIRED_CONTRACT','Two exact predicates distinguish fatal notification from nonfatal startup. Only that mixed case changes retained primary; overlapping PMD warning spans remain raw, and direct Error cannot be demoted to generic startup failure.'),
 (192,'CompareObjectsWithEquals'):(1,'REQUIRED_CONTRACT','Notification identical to startup primary must not self-suppress; distinct notification can be retained. Reference identity is the Java Throwable relation, not business value equality.'),
 (196,'AvoidCatchingGenericException'):(2,'REQUIRED_CONTRACT','Prepared runtime close reports Error directly or its own fixed nonfatal wrapper with a first group cause. Catching both retains declared startup cleanup priority; native UNKNOWN group close does not return into this block.'),
 (200,'AvoidInstanceofChecksInCatchClause'):(2,'REQUIRED_CONTRACT','Exact closing Error bypasses wrapper unwrapping; nonfatal closing is the internally guaranteed fixed wrapper/cause. Two overlapping spans reflect one necessary fatal-type decision, not an arbitrary subtype switch.'),
 (202,'CompareObjectsWithEquals'):(1,'REQUIRED_CONTRACT','The unwrapped actual cleanup cause is suppressed only when not identical to retained startup. Reference identity prevents a self-edge, without invoking arbitrary Throwable.equals.'),
 (221,'AvoidSynchronizedStatement'):(1,'REQUIRED_CONTRACT','Private final closeLock serializes group success caches and final completion after stopping is atomically published. It is not this/class/user lock. Unknown close cannot mark group/whole completion; start uses a not-yet-published prepared runtime.'),
 (235,'AvoidCatchingGenericException'):(2,'REQUIRED_CONTRACT','Each registered AutoCloseable group is closed in reverse and only successful phases cached. Exception/Error must be distinguished and reported; normal component accumulates failures while native group policy retains its exact UNKNOWN frame.'),
 (236,'AvoidInstanceofChecksInCatchClause'):(1,'REQUIRED_CONTRACT','Fatal group-close Error replaces a nonfatal accumulated failure, then is rethrown directly. The required fatal classification cannot be represented by wrapping every Throwable as successful cleanup.'),
 (238,'CompareObjectsWithEquals'):(1,'REQUIRED_CONTRACT','Distinct later close failures may be suppressed on the retained failure; identical Throwable is excluded to prevent self-suppression. This is an ownership/exception graph identity relation.')}
}
CASES={
 'ArtemisConnectionFactoryProvider':('dev.codex.schubert.nk.api.messaging.config.ApiFactoryNativeRetentionTest',),
 'ApiBrokerContexts':('dev.codex.schubert.nk.api.file.ApiBrokerContextsCredentialTest','dev.codex.schubert.nk.api.messaging.inbound.ApiNativeRetentionTest'),
 'WebBrokerContexts':('dev.codex.schubert.nk.api.file.WebBrokerContextsCredentialTest','dev.codex.schubert.nk.web.messaging.WebFactoryNativeRetentionTest'),
 'ApiMessagingRuntime':('dev.codex.schubert.nk.api.messaging.inbound.ApiNativeRetentionTest',)}


def calculate():
    raw=inspect.getsource(prior.calculate)
    raw=raw.replace("spec={'ServiceProcessResources':CORE,'ApiManagementServer':API,'WebNativeRuntime':WEB}",'spec=SPEC')
    start=raw.index("        testclass=");end=raw.index('        decisions.append',start)
    raw=raw[:start]+"        refs=[c for c in cases if c['className'].startswith(CASES[name])]\n        if not refs:raise ValueError('current original selected component XML references')\n"+raw[end:]
    raw=raw.replace('len(decisions)!=44','len(decisions)!=56').replace('all44','all56').replace('reviewed=44','reviewed=56')
    raw=raw.replace('1322 individual','1322 additional individual')
    scope={**vars(prior),'PLAN':prior.BASE/'PG6218-keeper-static-review-v1/manifest.json',
        'PLAN_SHA':'1548031591f786d0e6d1e2410e65c51b18443c29b2dd2f73869bcb0ded723d5a','SPEC':SPEC,'CASES':CASES}
    exec(compile(raw,'<56 source-specific JMS sites>','exec'),scope)
    return scope['calculate']()


def main():
    rows,value=calculate();os.umask(0o077);out=prior.BASE/'PG6222-jms-static-review-v1';out.mkdir()
    for name,body in [('decisions.json',rows)]:
        with (out/name).open('x') as f:
            json.dump(body,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value['decisionsSha256']=prior.sha(out/'decisions.json')
    with (out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,reviewed=56,statusCounts=value['statusCounts'],manifestSha256=prior.sha(out/'manifest.json'))))


if __name__=='__main__':main()
