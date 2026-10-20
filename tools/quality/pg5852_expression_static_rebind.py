"""Exact482 unchanged reasons after six expression owners, old whole remains historical only."""
import inspect
import pg5784_current_static_rebind as previous

SOURCE='86287c3fb83b483050b88dce04bc644961682bc4'


def reader_source():
    raw=inspect.getsource(previous.main)
    changes={
      'PG5772-primary-capture27-v1/manifest.json':'PG5846-current-static3967-v3/manifest.json',
      'b22a70787187534deadba238364e708c3fd749ceb456392795b5e11a81cff487':'f42681dbfd498db8a13b9374d0d2c94c9cddc149fea8f83597ce0d90b0491a9d',
      'PG5754-current3932-cases/qualification.json':'PG5832-current3967-cases/qualification.json',
      'ac4d3ccf6e9be8c1222aec8d09dd17508975f6475b3380faced765ce4c836b18':'fcceece52ccd16cf81f0b0e67060464ce0414a723417d2f827b8e29a9bcd9023',
      'PG5776-jms-primary-static-v1/manifest.json':'PG5848-protocol-expression-static-v1/manifest.json',
      'aa0368e648a0d1e25d2413e9aa8c08966a30feeea5ea87b3841e78fc66abf72f':'3c2ce6616b6b050543ec7ab9e580f2f2890d8bbf58fc7597da35a913c2f24100',
      '207c64bdb95dedd001056d79318acf1ff6c53ec00b7c17d55e3ba3bd9530c186':'dd25ce1a61a9c3136f0cdce90d1689f084463ecc962fabfb763504f69c61c0d8',
      'pg5776-jms-primary-static-v1/manifest.safe.json':'pg5848-protocol-expression-static-v1/manifest.safe.json',
      "if len(rows)!=1585 or len(used)!=472 or len(held)!=1 or not held[0]['sourcePath'].endswith('/ArtemisReplyConsumer.java')or held[0]['rule']!='CompareObjectsWithEquals':raise ValueError('only exact472 unchanged and one moved/changed owner scope held')":"if len(rows)!=1586 or len(used)!=482 or held:raise ValueError('all482 require exact source/coordinates/all owner byte; no moved scope imported')",
      "len({r['findingId']for r in rows})!=1585":"len({r['findingId']for r in rows})!=1586", "'currentRawFindings':1585":"'currentRawFindings':1586"}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('one current expression reauth binding')
        raw=raw.replace(old,new,1)
    compile(raw,'<current482 unchanged proof, no old PT transfer>','exec');return raw


def main():
    scope={**vars(previous),'SOURCE':SOURCE,'OLD_SOURCE':'6b5cea563b6f68b0b604afc06490063793e49662','OUT':previous.BASE/'PG5852-expression-dispositions-v1'}
    exec(compile(reader_source(),'<current482 unchanged proof>','exec'),scope)
    return scope['main']()


if __name__=='__main__':main()
