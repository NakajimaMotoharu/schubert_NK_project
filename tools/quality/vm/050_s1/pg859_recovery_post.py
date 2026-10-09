"""Independent complete-original failed recovery post; no stop/revoke/runtime replay."""
import ast,inspect
import pg784_stopped_baseline as transport
from pg814_recovery_post import PAYLOAD as previous
from pg856_sources_v2 import bind
from pg856_sources import EPOCH
from pathlib import Path
def payload():
    raw=bind(previous).replace('pg814-recovered949-post-v1','pg859-completed-failed-post-v1')
    raw=raw.replace('existingPairRetired=true','intentRetirement0=true').replace('==554','==564').replace("'batchRows':554","'batchRows':564")
    raw=raw.replace("intent=startup+'/0eece14c-f832-47c2-b7dd-14125682e7ea.API.start.intent'","intent=startup+'/"+EPOCH+".API.start.intent'")
    raw=raw.replace("set(before['trees'][startup])-{intent}and len(trees[startup])-1==43","set(before['trees'][startup])and len(trees[startup])-1==47")
    raw=raw.replace("'startupEntries':43","'startupEntries':47")
    raw='SCHEMA='+repr((Path(__file__).resolve().parent/'pg785_exec_history.py').read_text())+'\n'+raw
    ast.parse(raw);return raw
if __name__=='__main__':
    raw=inspect.getsource(transport.main).replace('pg784-stopped-current-v1','pg859-completed-failed-post-v1')
    namespace={**transport.__dict__,'PAYLOAD':payload()}
    exec(compile(raw,'<859 independent full24 current post>', 'exec'),namespace);namespace['main']()
