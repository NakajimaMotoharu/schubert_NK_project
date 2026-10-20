"""Reauthenticate unchanged474 reasons only; eight changed receiver reasons remain held."""
import pg5852_expression_static_rebind as previous
from pg5860_terminal_whole import SOURCE


def reader_source():
    raw=previous.reader_source()
    changes={
      'PG5848-protocol-expression-static-v1/manifest.json':'PG5858-terminal-static-v1/manifest.json',
      '3c2ce6616b6b050543ec7ab9e580f2f2890d8bbf58fc7597da35a913c2f24100':'4e5b6cb920bbc01334c6d1ef81f0042db10ca9fe5bbce8a920e2d7bd770cccdf',
      'dd25ce1a61a9c3136f0cdce90d1689f084463ecc962fabfb763504f69c61c0d8':'4dbb11979f1a8d7fdd6bbecabea207d8c2d6c7347d05d64ccce69f1e03e6d57c',
      'pg5848-protocol-expression-static-v1/manifest.safe.json':'pg5858-terminal-static-v1/manifest.safe.json',
      "if len(rows)!=1586 or len(used)!=482 or held:raise ValueError('all482 require exact source/coordinates/all owner byte; no moved scope imported')":"if len(rows)!=1586 or len(used)!=474 or len(held)!=8 or {r['sourcePath'].rsplit('/',1)[-1]for r in held}!={'SyncRequestConsumers.java','QuestionWorkConsumers.java','WebLogConsumers.java','ArtemisReplyConsumers.java'}:raise ValueError('474 exact reasons only; eight changed receiver guards held')"}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('one exact current terminal static binding')
        raw=raw.replace(old,new,1)
    compile(raw,'<474 same bytes and eight held, no old PT import>','exec');return raw


def main():
    scope={**vars(previous.previous),'SOURCE':SOURCE,'OLD_SOURCE':'6b5cea563b6f68b0b604afc06490063793e49662','OUT':previous.previous.BASE/'PG5868-terminal-dispositions-v1'}
    exec(compile(reader_source(),'<current474 unchanged reasons>','exec'),scope)
    return scope['main']()


if __name__=='__main__':main()
