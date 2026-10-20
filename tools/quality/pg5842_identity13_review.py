"""Recheck twelve moved guards and one new isolation constructor, never old PT/native import."""
import inspect
import re
import pg5820_identity14_review as previous
from pg5832_isolation_whole import SOURCE


def guarded_identity(text,fact,constructor=False):
    if not constructor:return previous.guarded_identity(text,fact,False)
    if fact['method']!='<init>'or fact['operator']!='NOT_EQUAL_TO'or(fact['leftExpression'],fact['rightExpression'])!=('protocolFailure','primary')or fact['firstLine']!=fact['lastLine']:raise ValueError('exact fresh isolation constructor reference pair')
    lines=text.splitlines(keepends=True);start=sum(map(len,lines[:int(fact['firstLine'])-1]))+int(fact['firstColumn'])-1;end=sum(map(len,lines[:int(fact['lastLine'])-1]))+int(fact['lastColumn'])
    if re.sub(r'\s+','',text[start:end])!='protocolFailure!=primary'or re.search(r'\bif\s*\(\s*$',text[:start])is None or re.match(r'\s*\)\s*\{\s*addSuppressed\(protocolFailure\);',text[end:])is None:raise ValueError('exact condition and direct diagnostic append, no callback or mutation')
    if 'Objects.requireNonNull(primary, "primary failure")'not in text[:start]or'Objects.requireNonNull(protocolFailure, "protocol failure")'not in text[:start]:raise ValueError('both invariants established before guard')
    return 'FRESH_ISOLATION_WRAPPER_CAUSE_NODE_DEDUPLICATION'


def reader_source():
    raw=inspect.getsource(previous.main)
    changes={
      'PG5816-current-dispositions-v1/manifest.json':'PG5838-current-dispositions-v1/manifest.json',
      '7faf04eb1070ed49c2284a75ec361e7f67f1374a2ba7c55e30a11aac9722c5c8':'8e66560d79ead924370a4b0e8dbd161fd81d0c757b24fbbe23beb70b201e8b71',
      'PG5798-lifetime-empty4-v1/manifest.json':'PG5824-current-static3955-v1/manifest.json',
      'dd2928921bae7193dcd95e1a604a85393abb3d8554a944247ebb8b6dd4e22c5c':'4ecc6dc8e7737d64efe61e39dda5060cab6d19ccff0ffa2951bffb0557ed6847',
      '2bbb85a297d7f7bd1b0c243d343e0da509faf99a':'2e3b0d50679ad6f1a984e25bd400db6f3ad9e798',
      'pg5818-current-reference-facts-v1':'pg5840-current-reference-facts-v1',
      '7a30e3ed84fcacdb928317fec8a9182aa9fbdbd2e426f590be3123de15df72a4':'73bf3e0917421ff4897f6b765bcf75805b68ed640cf153c1fe826a35fac69344',
      'pg5810-rollback-static-reauth-v1':'pg5830-isolation-static-v1',
      'PG5812-current-rollback54-v1/manifest.json':'PG5831-isolation66-v1/manifest.json',
      'b822a415878f1794b30f27320bbfc1353afd6b7aaa8b07dd7fed25bb5402b797':'c6244a36c37c2101c0625c911b35cc94f196b490186414ff034ffcc3d21a4057',
      "endswith('/UnconfirmedJmsRollbackException.java')":"endswith('/FailedJmsIsolationException.java')",
      "'PT-JMS-UNC'+str(i).zfill(3)for i in range(5,9)":"'PT-JMS-ISO'+str(i).zfill(3)for i in range(9,13)",
      'protocol:protocol/transport/UnconfirmedJmsRollbackException':'protocol:protocol/transport/FailedJmsIsolationException',
      "len(used)!=13 or new!=1 or len(decisions)!=14":"len(used)!=12 or new!=1 or len(decisions)!=13",
      'PG5820-identity14-v3':'PG5842-identity13-v1',
      "-=14":"-=13", "+=14":"+=13", "'rawFindings':1595":"'rawFindings':1594",
      "'recheckedChangedPrior':13":"'recheckedChangedPrior':12",
      'PG-D440/441; SS321/352':'PG-D440/442; SS321/322/352',
      'PG-D441; SS321/352. This fresh wrapper retains primary as its cause; only a distinct rollback Throwable becomes an additional diagnostic node.':'PG-D442; SS322/352. This fresh wrapper retains isolation/unknown-rollback primary as its cause; only a distinct protocol Throwable becomes an additional diagnostic node.'}
    for old,new in changes.items():
        if old not in raw:raise ValueError('exact current13 review binding: '+old)
        raw=raw.replace(old,new)
    compile(raw,'<current12 moved guards and new isolation constructor>','exec');return raw


def main():
    scope={**vars(previous),'SOURCE':SOURCE,'guarded_identity':guarded_identity}
    exec(compile(reader_source(),'<current13 identity review>','exec'),scope)
    return scope['main']()


if __name__=='__main__':main()
