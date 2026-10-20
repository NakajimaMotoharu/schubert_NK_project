"""Exact467 prior source/type/class reasons reauthenticated; thirteen changed owners held."""
import inspect
import pg5784_current_static_rebind as previous
from pg5808_rollback_whole import SOURCE


def rebind_source():
    raw=inspect.getsource(previous.main)
    replacements={
      "PG5772-primary-capture27-v1/manifest.json":"PG5798-lifetime-empty4-v1/manifest.json",
      'b22a70787187534deadba238364e708c3fd749ceb456392795b5e11a81cff487':'dd2928921bae7193dcd95e1a604a85393abb3d8554a944247ebb8b6dd4e22c5c',
      'PG5754-current3932-cases/qualification.json':'PG5780-current3939-cases/qualification.json',
      'ac4d3ccf6e9be8c1222aec8d09dd17508975f6475b3380faced765ce4c836b18':'1a5a5db819bde6bf01c85b4bb43017b8aae15bd59407b66adfbc4f5a0ca23c45',
      'PG5776-jms-primary-static-v1/manifest.json':'PG5810-rollback-static-reauth-v1/manifest.json',
      "rp=sp.with_name('findings.json')":"rp=BASE/'PG5804-rollback-static-v1/findings.json'",
      'aa0368e648a0d1e25d2413e9aa8c08966a30feeea5ea87b3841e78fc66abf72f':'68b697ad9162315810ccc0c4adb0cceb200dc60ca44c8686750998742cea5c23',
      '207c64bdb95dedd001056d79318acf1ff6c53ec00b7c17d55e3ba3bd9530c186':'5473015a6d62f0edc3d2bb4af665bdfa5f0409a73b10da060f9403552276c92d',
      'pg5776-jms-primary-static-v1/manifest.safe.json':'pg5810-rollback-static-reauth-v1/manifest.safe.json',
      "if len(rows)!=1585 or len(used)!=472 or len(held)!=1 or not held[0]['sourcePath'].endswith('/ArtemisReplyConsumer.java')or held[0]['rule']!='CompareObjectsWithEquals':raise ValueError('only exact472 unchanged and one moved/changed owner scope held')":"if len(rows)!=1595 or len(used)!=467 or len(held)!=13 or any(r['rule']!='CompareObjectsWithEquals'for r in held):raise ValueError('only exact467 unchanged, thirteen changed/moved identity scopes held')",
      "len({r['findingId']for r in rows})!=1585":"len({r['findingId']for r in rows})!=1595",
      "'currentRawFindings':1585":"'currentRawFindings':1595"}
    for old,new in replacements.items():
        if raw.count(old)!=1:raise ValueError('exact current reauthentication binding: '+old)
        raw=raw.replace(old,new,1)
    raw=raw.replace('all849 current source','all850 current source')
    compile(raw,'<current467 complete source and actual byte binding>','exec');return raw


def main():
    scope={**vars(previous),'SOURCE':SOURCE,'OLD_SOURCE':'2bbb85a297d7f7bd1b0c243d343e0da509faf99a','OUT':previous.BASE/'PG5816-current-dispositions-v1'}
    exec(compile(rebind_source(),'<current467 complete source and byte binding>','exec'),scope)
    return scope['main']()


if __name__=='__main__':main()
