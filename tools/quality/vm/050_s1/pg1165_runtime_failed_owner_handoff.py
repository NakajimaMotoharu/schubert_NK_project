"""SSC260 fixed wrong-runtime owner once TERM, preserve loaded runtime/raw."""
import ast
import inspect
import pg1157_native_failed_owner_handoff as previous


def source():
    s=inspect.getsource(previous)
    for old,new in [('from pg1155_native_failed_owner_proof_v3 import payload as previous','from pg1164_runtime_failed_owner_proof import payload as previous'),
                    ('pg1155-native-failed-owner-proof-v3.safe.json','pg1164-runtime-failed-owner-proof-v1.safe.json'),
                    ('f8915d10930682d7942d52b1fd97fc091edb563f0b426c4d8bf7633cdda5da51','8f0794b3466ea22bbff455b907788ed7976a3c4869b2ed7b7452a84acdc971d5'),
                    ('native-failed-owner-proof-v3','runtime-failed-owner-proof-v1'),('native-failed-owner-handoff-v1','runtime-failed-owner-handoff-v1'),
                    ('410279','415524'),('4653404','4807423'),('410308','415553'),('4653520','4807540'),
                    ('98f1a3a4ae2d298e8eae985059cf6a30f3f203fbb5ede0ec95350b3ab9f15791','dff614fe6734a813f68a6c816bce48da90749373d222093c8a952d30b8764e5a'),
                    ('pg1157-native-failed-owner-handoff-v1','pg1165-runtime-failed-owner-handoff-v1'),
                    ('PG1157-native-failed-owner-handoff-v1','PG1165-runtime-failed-owner-handoff-v1')]:s=s.replace(old,new)
    s=s.replace('pg1157-runtime-failed-owner-handoff-v1','pg1165-runtime-failed-owner-handoff-v1').replace('PG1157-runtime-failed-owner-handoff-v1','PG1165-runtime-failed-owner-handoff-v1')
    marker='    text=text[:text.index(marker)]+body'
    if s.count(marker)!=1:raise ValueError('fixed runtime current closure insertion refused')
    s=s.replace(marker,"    a=body.index('def current():');b=body.index('def child_before(',a);body=body[:a]+body[b:]\n"+marker)
    ast.parse(s);return s


if __name__=='__main__':exec(compile(source(),'<once fixed runtime owner handoff>','exec'),{'__name__':'__main__','__file__':__file__})
