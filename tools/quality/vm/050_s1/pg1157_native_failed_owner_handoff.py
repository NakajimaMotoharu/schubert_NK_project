"""Exact failed native child then Java once pidfd TERM; no business mutation."""
import ast
import inspect
import json
from pg1155_native_failed_owner_proof_v3 import payload as previous
from pg1142_fixed_failed_owner_handoff import BODY as handoff
from pg1041_cold_policy_diagnostic import W
import pg1026_cold_observation_contract as contract
import pg1120_current_failed_capture as transport


def payload():
    proof=json.loads((W/'pg1155-native-failed-owner-proof-v3.safe.json').read_bytes())
    if proof['actualExit']!=0 or proof['privateSnapshotSha256']!='f8915d10930682d7942d52b1fd97fc091edb563f0b426c4d8bf7633cdda5da51':raise ValueError('fixed complete native owner proof refused')
    text=previous().replace('native-failed-owner-proof-v3','native-failed-owner-handoff-v1')
    marker='bus=dbus.SystemBus(private=True);manager=dbus.Interface'
    body=handoff
    for old,new in [('failed-owner-preflight-v1','native-failed-owner-proof-v3'),('6119d517c5880b95815b03a32c35bc15627489aebb52fa26925195d9bcdcbc64','f8915d10930682d7942d52b1fd97fc091edb563f0b426c4d8bf7633cdda5da51'),('404585','410279'),('4248646','4653404'),('404614','410308'),('4248757','4653520'),('61d39d9b14028d6861a43af6b68502107d5b30a8c5c7ec8eeedd2e715f6d8207','98f1a3a4ae2d298e8eae985059cf6a30f3f203fbb5ede0ec95350b3ab9f15791'),('actor_proof(','actor('),('cleanupStillOriginalActiveExited','nativeStillOriginalUnchanged')]:body=body.replace(old,new)
    body=body.replace('before=whole();require(before==PROVEN==whole())','owned_snapshot=whole();require(owned_snapshot==PROVEN==whole())').replace('json.dump(before,f,sort_keys=True)','json.dump(owned_snapshot,f,sort_keys=True)')
    text=text[:text.index(marker)]+body
    definitions=[n for n in ast.parse(inspect.getsource(contract)).body if isinstance(n,ast.FunctionDef)and n.name in {'durable_reservation','terminate_once'}]
    if len(definitions)!=2:raise ValueError('fixed tested once termination contract refused')
    snippet='import os,re\n'+ast.unparse(ast.Module(body=definitions,type_ignores=[]))
    text="import signal,select,time,types\ncontract=types.ModuleType('fixed-native-once-contract')\nexec("+repr(snippet)+",contract.__dict__)\nSIGNALS=0\n"+text
    ast.parse(text);return text


def main():
    text=inspect.getsource(transport.main).replace('pg1120-current-failed-capture-v1','pg1157-native-failed-owner-handoff-v1').replace('PG1120-current-failed-capture-v1','PG1157-native-failed-owner-handoff-v1')
    env=dict(transport.__dict__);env['PAYLOAD']=payload();exec(compile(text,'<fixed native once owner handoff>','exec'),env);return env['main']()


if __name__=='__main__':raise SystemExit(main())
