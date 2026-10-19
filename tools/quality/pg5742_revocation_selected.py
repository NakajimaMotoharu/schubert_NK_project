"""Normal finite synthetic revocation codec PT; no deployed credentials or environment access."""
import inspect
import pg5732_enum48_selected as previous

SLOT='pg5742-revocation-selected-v1'


def main():
    raw=inspect.getsource(previous.main)
    replacements={
      "count=3 if module=='protocol'else 4 if module=='web'else 1":"count=3 if module=='protocol'else 7 if module=='web'else 1",
      'sum(map(len,expected.values()))!=12':'sum(map(len,expected.values()))!=15',
      "'expectedTests':12":"'expectedTests':15"}
    for old,new in replacements.items():
        if raw.count(old)!=1:raise ValueError('exact original finite inventory predicate')
        raw=raw.replace(old,new,1)
    namespace={**vars(previous),'SLOT':SLOT,'CASES':{**previous.CASES,'web':{'web.revocation.RevocationPayloadCodecTest'}}}
    exec(compile(raw,'<explicit original seven synthetic revocation fixtures>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
