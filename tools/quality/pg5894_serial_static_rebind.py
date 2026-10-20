"""Exact523 same-source/coordinate/owner-byte reasons, changed five remain held."""
import inspect
import pg5784_current_static_rebind as previous
from pg5886_terminal_serial_whole import SOURCE
from pg5882_terminal_serial_static import MODIFIED

IDENTITY=('findingId','sourcePath','sourceSha256','rule','beginline','endline','begincolumn','endcolumn','diagnosticTextSha256')


def bind_current(row,candidates,raw,before,current):
    if len(candidates)>1:
        exact=[c for c in candidates if all(c.get(k)==row.get(k)for k in IDENTITY)]
        if len(exact)==1:candidates=exact
    return previous.bind_one(row,candidates,raw,before,current)


def reader_source():
    raw=inspect.getsource(previous.main)
    changes={'PG5772-primary-capture27-v1/manifest.json':'PG5876-current-static3971-v1/manifest.json','b22a70787187534deadba238364e708c3fd749ceb456392795b5e11a81cff487':'3c90000fad14ffdc5ab032596bfcf6f85ecef199c987b10967228ea133bff06f','PG5754-current3932-cases/qualification.json':'PG5860-current3971-cases/qualification.json','ac4d3ccf6e9be8c1222aec8d09dd17508975f6475b3380faced765ce4c836b18':'a937e6dc41450d13b2874299d28f19caafc5b0b070fffdd4c96669bc410c3d02','PG5776-jms-primary-static-v1/manifest.json':'PG5882-terminal-serial-static-v1/manifest.json','aa0368e648a0d1e25d2413e9aa8c08966a30feeea5ea87b3841e78fc66abf72f':'2b5a42b051c804000affd8b92ea51c51c4e6dcf8e21addbed975a966335b7ec8','207c64bdb95dedd001056d79318acf1ff6c53ec00b7c17d55e3ba3bd9530c186':'a7d670b5425444929c6f0e09294b7145b920f394929c19cf5829aa7168a61bf1','pg5776-jms-primary-static-v1/manifest.safe.json':'pg5882-terminal-serial-static-v1/manifest.safe.json',"if len(rows)!=1585 or len(used)!=472 or len(held)!=1 or not held[0]['sourcePath'].endswith('/ArtemisReplyConsumer.java')or held[0]['rule']!='CompareObjectsWithEquals':raise ValueError('only exact472 unchanged and one moved/changed owner scope held')":"if len(rows)!=1586 or len(used)!=523 or len(held)!=5 or any(r['sourcePath']not in MODIFIED for r in held):raise ValueError('523 exact prior reasons only; five changed receiver guards held')","len({r['findingId']for r in rows})!=1585":"len({r['findingId']for r in rows})!=1586","'currentRawFindings':1585":"'currentRawFindings':1586"}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('one current serial rebind source/hash binding')
        raw=raw.replace(old,new,1)
    compile(raw,'<523 exact reasons and five held>','exec');return raw


def main():
    scope={**vars(previous),'SOURCE':SOURCE,'OLD_SOURCE':'0f572da66c9e3f0818cddb5bf679e7b8bc0f47da','MODIFIED':MODIFIED,'bind_one':bind_current,'OUT':previous.BASE/'PG5894-serial-dispositions-v1'}
    exec(compile(reader_source(),'<523 current unchanged reasons>','exec'),scope)
    return scope['main']()


if __name__=='__main__':main()
