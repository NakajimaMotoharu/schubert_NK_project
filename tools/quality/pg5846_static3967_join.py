"""Join pending482 only to genuine same-source3967 XML; no execution or analyzer replay."""
import inspect
import json
import pg5824_static3955_join as previous
from pg5832_isolation_whole import SOURCE,W
from pg5540_snapshot_scratch_selected import sha
from static_disposition_overlay import BASE


def validate_cases(cases,q):
    if len(cases)!=3967 or len({c['testId']for c in cases})!=3967 or any(c['result']!='PASS_ORIGINAL_XML'or c['xmlSha256']!=q['modules'][c['module']]['xmlHashes'][c['sourceXml']]for c in cases):raise ValueError('all3967 actual case references from exact qualified XML')


def qualified_whole():
    qp=BASE/'PG5832-current3967-cases/qualification.json';cp=qp.with_name('cases.json');q=json.loads(qp.read_bytes());cases=json.loads(cp.read_bytes());rp=W/'pg5834-isolation-qualified-v1/manifest.safe.json';r=json.loads(rp.read_bytes());op=W/'pg5832-isolation-six-v1/manifest.safe.json';original=json.loads(op.read_bytes());staticp=W/'pg5830-isolation-static-v1/manifest.safe.json';static=json.loads(staticp.read_bytes())
    if not(q['productionSource']==r['source']==original['source']==static['source']==SOURCE and q['projectionActualExit']==r['actualExit']==original['actualExit']==0 and q['qualificationReceiptSha256']==sha(rp)and r['originalReturnedManifestSha256']==sha(op)and q['casesSha256']==sha(cp)and q['serverManifestSha256']==r['result']['serverManifestSha256']and q['allPhysicalMainSha256']==r['result']['allPhysicalMainSha256']==static['auxClassHashes']and(q['tests'],q['suites'],q['mainClasses'])==(3967,590,1666)and q['FESFlakyNotRun']==q['staticSixModules']==0 and q['wholeReplayed']is False):raise ValueError('genuine original3967 independently qualified and projected, no borrowed success')
    if any(q[k]!=v for k,v in r['result'].items()):raise ValueError('projection preserves the entire independent result')
    validate_cases(cases,q)
    return qp,cp,q,cases


def reader_source():
    raw=inspect.getsource(previous.main)
    changes={
      "PG5820-identity14-v3/manifest.json":"PG5842-identity13-v1/manifest.json",
      'a64aaa208d14e5b519dc5e11df7bdb2a449e180e9743ed86ac066089790c5b4c':'fb83060cebecc1dc1ad27eeb0c17d2e54d61ffe4d27377e63b4a0d0988f5ced1',
      'PG5780-current3939-cases/qualification.json':'PG5808-current3955-cases/qualification.json',
      '1a5a5db819bde6bf01c85b4bb43017b8aae15bd59407b66adfbc4f5a0ca23c45':'42bdfb97cdc1f3b1944e28e144e91993ed2f05bc269a289ba6f20e6d7f29a376',
      '6b8489660ecb397be6e020893eb3257df216ed5845923c4c93c832451b99bfbb':'53e4c0275a33d18a408f9ca86851b1ae8fd12e1d1d22aab13d8899b8dc513dc6',
      'joined!=481':'joined!=482','len(result)!=1595':'len(result)!=1594',
      'PG5824-current-static3955-v1':'PG5846-current-static3967-v1',
      "'currentWholeTests':3955":"'currentWholeTests':3967", "'currentRawFindings':1595":"'currentRawFindings':1594"}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('one current482 original XML join binding')
        raw=raw.replace(old,new,1)
    compile(raw,'<current482 to original3967 join>','exec');return raw


def main():
    scope={**vars(previous),'SOURCE':SOURCE,'W':W,'validate_cases':validate_cases,'qualification_source':lambda:inspect.getsource(qualified_whole)}
    exec(compile(reader_source(),'<current482 to original3967 join>','exec'),scope)
    return scope['main']()


if __name__=='__main__':main()
