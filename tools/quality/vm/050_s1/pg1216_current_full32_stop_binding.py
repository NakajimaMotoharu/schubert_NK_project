"""Current genuine root plus fresh full32 normal recovery before image."""
import ast
import pg1208_current_stop_v2_binding as old
SOURCE=old.SOURCE
BEFORE=old.BEFORE
OWNED=old.OWNED
FULL32='bc98f52bd67e7b32f54a85d55bf7d8ceb08b97ca6891d081d192d4a4afab935a'
BEFORE_PATH='/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/full32-stop-owner-handoff-v1/after.private.json'


def bindings(proof):
    if type(proof)is not dict or proof.get('full32RecoveryAfterSha256')!=FULL32 or proof.get('full32RecoveryActualExit')!=0:
        raise ValueError('actual new full32/all resource post required')
    return old.bindings(proof)


def generate(proof):
    bindings(proof)
    values={name.replace('1208','1216'):raw.replace('Pg1208','Pg1216').replace('PG1208','PG1216').replace('pg1208','pg1216')for name,raw in old.generate(proof).items()}
    refs=values['pg1216_native_refs.py']
    previous='/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/completed-current-before-v1/before.private.json'
    if refs.count(previous)!=2 or refs.count(BEFORE)!=1:raise ValueError('fixed actual full32 refs source insertion refused')
    values['pg1216_native_refs.py']=refs.replace(previous,BEFORE_PATH).replace(BEFORE,FULL32)
    for name,raw in values.items():
        if name.endswith('.py'):ast.parse(raw)
    return values
