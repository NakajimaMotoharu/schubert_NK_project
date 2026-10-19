"""Publish only original completed protocol PT and independent static evidence."""
import inspect
import pg5727_protocol_public as previous
from pg5728_protocol27 import SLOT as PROTOCOL


def main():
    raw=inspect.getsource(previous.main)
    replacements={
      'PG5726-enum-static-v1':'PG5729-protocol27-static-v1',
      'target18StaticAndAbiQualified':'target27StaticAndAbiQualified',
      'PG5727-protocol88-enum18':'PG5730-protocol88-enum27',
      '1181_semantic_enum内部命名是正・互換単体テスト仕様.md':'1183_protocol残九field是正・通常PT仕様.md',
      "bugs=['BUG1474','BUG1475'],crossCheck='YKT1237/YKT1238'":"bugs=['BUG1476'],crossCheck='YKT1237'",
      "PTALT-001 remains unresolved and unrelated to this executed subset":"PTALT-001/002 unresolved; this subset is ordinary executed PT"}
    for old,new in replacements.items():
        if raw.count(old)!=1:raise ValueError('exact reviewed publication replacement')
        raw=raw.replace(old,new,1)
    namespace={**vars(previous),'PROTOCOL':PROTOCOL}
    exec(compile(raw,'<original completed protocol27 evidence publication>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':main()
