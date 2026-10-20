"""Reauthenticate old481 only with exact source/coordinates/all owner bytes; never import old PT."""
import inspect
import pg5784_current_static_rebind as previous
from pg5832_isolation_whole import SOURCE
from pg5830_isolation_static import MODIFIED


def reader_source(findings_sha):
    raw=inspect.getsource(previous.main)
    changes={
      'PG5772-primary-capture27-v1/manifest.json':'PG5824-current-static3955-v1/manifest.json',
      'b22a70787187534deadba238364e708c3fd749ceb456392795b5e11a81cff487':'4ecc6dc8e7737d64efe61e39dda5060cab6d19ccff0ffa2951bffb0557ed6847',
      'PG5754-current3932-cases/qualification.json':'PG5808-current3955-cases/qualification.json',
      'ac4d3ccf6e9be8c1222aec8d09dd17508975f6475b3380faced765ce4c836b18':'42bdfb97cdc1f3b1944e28e144e91993ed2f05bc269a289ba6f20e6d7f29a376',
      'PG5776-jms-primary-static-v1/manifest.json':'PG5830-isolation-static-v1/manifest.json',
      'aa0368e648a0d1e25d2413e9aa8c08966a30feeea5ea87b3841e78fc66abf72f':'a8db12fed46184684ec8d911266dedac6206f42ca65be2fcd8f8c424ab6bbf8f',
      '207c64bdb95dedd001056d79318acf1ff6c53ec00b7c17d55e3ba3bd9530c186':findings_sha,
      'pg5776-jms-primary-static-v1/manifest.safe.json':'pg5830-isolation-static-v1/manifest.safe.json',
      "if len(rows)!=1585 or len(used)!=472 or len(held)!=1 or not held[0]['sourcePath'].endswith('/ArtemisReplyConsumer.java')or held[0]['rule']!='CompareObjectsWithEquals':raise ValueError('only exact472 unchanged and one moved/changed owner scope held')":"if len(rows)!=1594 or len(decided)!=481 or len(used)+len(held)!=481 or any(r['sourcePath']not in MODIFIED for r in held):raise ValueError('every old481 accounted; moved/changed source owners held without transfer')",
      "len({r['findingId']for r in rows})!=1585":"len({r['findingId']for r in rows})!=1594",
      "'currentRawFindings':1585":"'currentRawFindings':1594"}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('one immutable current reauth binding')
        raw=raw.replace(old,new,1)
    compile(raw,'<current source reason reauthentication>','exec');return raw


def main():
    path=previous.BASE/'PG5830-isolation-static-v1/findings.json';scope={**vars(previous),'SOURCE':SOURCE,'OLD_SOURCE':'2e3b0d50679ad6f1a984e25bd400db6f3ad9e798','MODIFIED':MODIFIED,'OUT':previous.BASE/'PG5838-current-dispositions-v1'}
    exec(compile(reader_source(previous.sha(path)),'<current851 source reason reauthentication>','exec'),scope)
    return scope['main']()


if __name__=='__main__':main()
