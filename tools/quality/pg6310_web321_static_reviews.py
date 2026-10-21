"""20 individually located current Web sender applicability spans; no raw suppression."""
import inspect
import json
import os
import pg6284_web_owned_static_reviews as engine
from pg6298_web_send_qualification import original_source

G='AvoidCatchingGenericException';I='AvoidInstanceofChecksInCatchClause';E='CompareObjectsWithEquals'
SPEC={
 'ArtemisRequestSender':{
 (61,G):(1,'Checked JMS and provider RTE stage/commit failure trigger the existing one rollback attempt and original rethrow. The new owned finally may promote a close Error; this catch does not convert Error to ordinary request failure.'),
 (65,G):(2,'Both unchecked primary spans record the exact acquired-context failure before finally. JMS/RTE/Error identity flows into owned close, not a successful response or fabricated commit. It does not own the caller correlation registry.'),
 (76,G):(1,'Secondary rollback RTE remains attached only to a distinct original failure; Error is not caught by this helper. Rollback is not proof of confirmed send or permission to issue another request.'),
 (77,E):(1,'Rollback can rethrow the same provider RTE. Reference inequality prevents self-suppression; provider equals would not express Throwable identity safely.'),
 (86,G):(2,'Both unchecked close spans protect the one owned context.close. No-primary closes retain their existing direct type; nonfatal primary plus Error promotes that Error, otherwise original primary is retained. Independent321001 matrix/source-JVM and original84 verify this narrow policy, not actual Root completion.'),
 (91,I):(1,'Direct cleanup Error must supersede only non-Error primary. These identities cannot be equal by type; original primary is retained suppressed on the fatal object. Other primary Error stays original.'),
 (95,E):(1,'Distinct reference guard excludes provider same-Throwable self-suppression. It applies after fatal priority and cannot manufacture a successful send.')},
 'WebLogMessageSender':{
 (57,G):(1,'Stage JMS/RTE triggers one rollback then fixed WebLogSendException with original cause. Wire authentication/decryption precedes acquisition; normal MessageID/property/duplicate contracts remain unchanged.'),
 (63,G):(1,'Commit RTE triggers existing rollback and only the exact typed cause/linked duplicate graph can confirm previous delivery. Suppressed cleanup is not duplicate evidence; unrelated failures remain typed unconfirmed.'),
 (69,G):(2,'Both unchecked body spans retain primary in the minimal manual owned scope. Direct Error stays fatal, typed/JMS transport failure stays non-success, and finally closes exactly once without relying on generated TWR self-suppression.'),
 (77,G):(1,'Only remaining RTE at the outer lifecycle boundary is mapped to the existing fixed WebLogSendException. The promoted/direct Error bypasses it; decrypt/open failure still wipes the acquired plaintext and does not close an unacquired context.'),
 (88,G):(2,'Both unchecked close spans implement the SS321 one-close/identity contract. Original84 independently covers no-primary/nonfatal/fatal, different/same Throwable and normal-body wipe; neither close failure nor computed body implies committed/closed success.'),
 (90,I):(1,'Cleanup Error over non-Error primary must escape as the identical Error, retaining the earlier failure suppressed. It cannot become a durable ordinary send-retry classification. Existing primary Error retains its identity.'),
 (94,E):(1,'The explicit reference identity guard replaces generated TWR self-suppression behavior. Same Error or RTE is never added to itself, avoiding IllegalArgumentException masking the primary.'),
 (101,G):(1,'Rollback RTE is secondary on an unconfirmed original failure, never a successful commit signal. This helper does not catch Error or retry rollback.'),
 (102,E):(1,'Provider may rethrow the same RTE from stage and rollback. Distinct-only suppression keeps original cause identity and avoids executing provider equals.')}
}
TESTS={
 'ArtemisRequestSender':['dev.codex.schubert.nk.web.messaging.ArtemisRequestSenderTest','dev.codex.schubert.nk.web.messaging.JmsRequestReplyClientTest'],
 'WebLogMessageSender':['dev.codex.schubert.nk.web.logging.WebLogMessageSenderTest','dev.codex.schubert.nk.web.logging.WebLogDispatcherTest','dev.codex.schubert.nk.web.logging.WebLogReplayWorkerTest']}


def calculate():
    scope={**vars(engine),'PLAN':engine.BASE/'PG6308-current4043-static-plan-v1/manifest.json',
        'PLAN_SHA':'9c5c52d27c09feedfa78be753bc2508d2c244e66c3e92d7348451df26fb645de',
        'SPEC':SPEC,'TESTS':TESTS,'original_source':original_source}
    raw=inspect.getsource(engine.calculate)
    for a,b in (('PG6268-outbox-failure-qualification-v1','PG6298-web-send-qualification-v1'),
        ('pg6268-outbox-failure-qualification-v1','pg6298-web-send-qualification-v1'),
        ('d4e587322de799db097dab934611431448b229953bae5838aa721b7c51ac0225','00b8f41991bf05c2aaf439cc502ecf6afba47f9247587684941ee168dbc75c27'),
        ('len(decisions)!=33','len(decisions)!=20'),('all33 explicit','all20 explicit'),('reviewed=33','reviewed=20'),
        ('rawFindings=1350','rawFindings=1357'),('1338 individual ordinary Web','1345 individual SS321 Web')):
        if a not in raw:raise ValueError('one explicit current84/static binding '+a)
        raw=raw.replace(a,b)
    exec(compile(raw,'<20 current Web321 spans>','exec'),scope)
    rows,value=scope['calculate']()
    value['unresolved']=['actual current4043 case binding pending','broader JDBC/TWR applicability/runtime/global quality remain separate, no blanket nonapplicability']
    return rows,value


def main():
    rows,value=calculate();os.umask(0o077);out=engine.BASE/'PG6310-web321-static-review-v1';out.mkdir()
    with(out/'decisions.json').open('x')as f:json.dump(rows,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value['decisionsSha256']=engine.sha(out/'decisions.json')
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,reviewed=20,statusCounts=value['statusCounts'],manifestSha256=engine.sha(out/'manifest.json'))))


if __name__=='__main__':main()
