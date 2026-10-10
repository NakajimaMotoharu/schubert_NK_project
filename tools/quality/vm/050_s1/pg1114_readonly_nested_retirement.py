"""SSC253 fixed134103 read-only before reservation retirement, not source replay."""
import ast
import hashlib
import json
from pg1110_readonly_once_retirement import payload as previous
from pg1051_cold_tree_preflight_v2 import dispatch
from pg1041_cold_policy_diagnostic import W


def payload():
    old=W/'pg1111-nested-ordinary-once-v1';begin=json.loads((old/'begin.safe.json').read_bytes())
    if begin['operatorSource']!='e8d815a0a6934d734f7b4e9c997fd085f5204b76'or begin['scriptSha256']!='55f4b085422d339b5a96784096938865df7e0fe30331e36ca1bc64b4e0d1620e':raise ValueError('fixed nested failed source refused')
    if hashlib.sha256((old/'guest-script.private.py').read_bytes()).hexdigest()!=begin['scriptSha256']or hashlib.sha256((old/'result.private.log').read_bytes()).hexdigest()!='51249e300665dcc00ccfd92ec2d0dc7849e1ec66f0773f9f0edf0a1221dcabb6':raise ValueError('fixed nested failed witness refused')
    raw=previous()
    for old,new in [('PG1110-readonly-once-retirement-v1','PG1114-readonly-nested-retirement-v1'),
      ('readonly-retirement-v1','readonly-nested-retirement-v1'),('20312','134103'),('3250518','3382984'),('20310','134100'),
      ('pg1108-ordinary-cold-once-v1','pg1106-ordinary-cold-before-v1/nested-once-v1')]:
        if old not in raw:raise ValueError('fixed nested retirement profile refused')
        raw=raw.replace(old,new)
    ast.parse(raw);return raw


if __name__=='__main__':dispatch('PG1114-readonly-nested-retirement-v1','pg1114-readonly-nested-retirement-v1',payload())
