"""Only qualified new1902/e016 diagnostic gap coordinates; no VM writes or old data."""
import ast
from pathlib import Path
from pg645_native_gap import code as previous
R=Path(__file__).resolve().parent
def code():
 raw=previous()
 for old,new in (
  ('pg644-current-eight-native-v1','pg879-current-eight-native-v1'),
  ('3200b4a2e5b5bd63a5854dbb541c22ca66cdb14bc98fde75173797a96bb68aa0','317dcf8f294d0b5099875a7566b9299666cb4e76a1797c16bd25f2393ca165f7'),
  ('36fe7a0b938489d61d17d49c1c30a6fbbef699d5','e01612fcd7f2752df5ae0836b78538fd5e87f120'),
  ('pg645-current-native-gap-v1','pg886-current-native-gap-v1'),
  ('pg630-retention-factory-six-host-v1','pg857-completed-reference-six-host-v1'),
 ):
  assert old in raw,old;raw=raw.replace(old,new)
 ast.parse(raw);return raw
if __name__=='__main__':
 env={'__name__':'current_e016_gap','__file__':str(R/'pg886_native_gap.py')};exec(compile(code(),'<886 current e016 gaps>','exec'),env);env['main']()
