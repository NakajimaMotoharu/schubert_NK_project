"""Separate finite runtime delta and full resource/original/native post, read-only."""
import pg1583_current_stop_independent_post as prior
import pg1236_completed_runtime_retired_post as old_post
from pg1591_current_runtime_retirement_sources import contract_source,SHA,BASE,SOURCE,TOOLS
from pg847_configuration import FIELDS

def payload(seals):
    raw=prior.payload(seals)
    raw=raw.replace('pg1579-native-stop-v1','pg1591-native-stop-v1').replace('pg1579-current-owned-stop-tools-v1',TOOLS)
    raw=raw.replace('allEightOwnedTerminal=true\\n','allTenAlreadyTerminal=true\\n').replace('starts0=true\\noldUnknownNormalized=false','starts0=true\\nruntimeRetiredOnly=true\\noldUnknownNormalized=false')
    marker="require(all(after[k]==before[k]for k in before if k not in ('units','configuration')))"
    contract=contract_source().replace('from pg847_configuration import FIELDS','FIELDS='+repr(FIELDS))
    original=old_post.ORIGINAL.replace('/var/lib/pgpt-s1-preservation/pg1216-native-stop-v1/after.private.json',BASE).replace('21505d35e87a01314e63a2b834d1570d0d96a4b02a5fe9af4c117c35c7867c36',SHA)
    check='import types\nretirement=types.ModuleType("current_exact_runtime");exec('+repr(contract)+',retirement.__dict__)\n'+original
    if raw.count(marker)!=1:raise ValueError('one exact finite runtime delta boundary required')
    raw=raw.replace(marker,check)
    raw=raw.replace('PG1583-current-terminal-post-v1','PG1595-current-runtime-retired-post-v1').replace('pg1583-current-terminal-post-v1','pg1595-current-runtime-retired-post-v1')
    raw=raw.replace("'normalCurrentOwnedStopScopesSealed':True","'normalCurrentRetirementScopesSealed':True,'runtimeExactEntryRetired':True")
    raw=raw.replace("'ownedExplicitStops':4,'eightTerminalReceipts':True","'ownedExplicitStops':0,'currentOriginalTerminalHistoryRetained':True")
    compile(raw,'<current exact runtime original and post>','exec');return raw

def source():
    raw=prior.source()
    for old,new in [('pg1581-stop-v1.exit','pg1594-retire-v1.exit'),('pg1580-frozen-v1.safe.json','pg1592-frozen-v1.safe.json'),
                    ("replace('1216','1579')","replace('1216','1591')"),('pg1579-current-owned-stop-tools-v1',TOOLS),
                    ('pg1579-native-stop-v1','pg1591-native-stop-v1'),('pg1579_parent_receipt.py','pg1591_parent_receipt.py'),
                    ('pg1583-current-terminal-post-v1','pg1595-current-runtime-retired-post-v1')]:
        if old not in raw:raise ValueError('actual current retirement host boundary absent')
        raw=raw.replace(old,new)
    compile(raw,'<current independent retirement post host>','exec');return raw

def main():
    env={**prior.prior.previous.transport.__dict__,'SOURCE':SOURCE,'payload':payload}
    exec(compile(source(),'<actual complete finite retirement post>','exec'),env);return env['main']()

if __name__=='__main__':raise SystemExit(main())
