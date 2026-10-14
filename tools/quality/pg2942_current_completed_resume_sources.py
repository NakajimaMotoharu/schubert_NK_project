"""New a9/79a completed-resume source graph; preparation only, not external Root start."""
import ast
import inspect
from pyflakes.api import check
import pg2304_current_completed_resume_sources as prior
import pg2890_network_owned_sources as current
from pg2814_network_newboot_readonly import BOOT
from pg2862_network_newcurrent_observer import SOURCE,BOM
import pg2943_runtime_parent_contract as parent_contract

TOOLS='pg2942-current-completed-resume-tools-v1'
SAVE='pg2946-current-completed-resume-preparation-v1'
CLASS='Pg2942FreshResumePreparation'
BEFORE='3ddd86e5fefbe30d96876a9e8fc9e149dc28e4ab5e00f314f62bf416ebe6ee32'
RUN='0dc63b79-3f9a-450c-b2a6-56f86272d272'


def bind(raw):
    pairs=[(prior.TOOLS,TOOLS),(prior.SAVE,SAVE),(prior.CLASS,CLASS),('pg2304','pg2942'),('Pg2304','Pg2942'),('PG2304','PG2942'),
        (prior.SOURCE,SOURCE),(prior.BOM,BOM),(prior.BEFORE,BEFORE),('PG2126','PG2802'),('pg2126','pg2802'),
        ('b2d6f605-61cf-425f-8fbd-12d606f6ee66',BOOT),('b2d6f60561cf425f8fbd12d606f6ee66',BOOT.replace('-','')),
        (prior.RUN,RUN),('9be93262-fbb2-438f-b2b0-c4a27f5563a4','74729e17-91c0-43e7-b01f-74f9e6461d6a'),
        ('2026-10-13T15:01:53.237266Z','2026-10-14T19:12:28.842213Z'),('2026-10-13T15:28:38.568622Z','2026-10-14T19:39:10.330316Z'),
        ('pg2274-native-stop-v1/after.private.json','pg2890-native-stop-v1/after.private.json'),
        ('2f23a5f7362a48958f1cb24ed3fde748','d4197711cfc54770a4ac7c8d90a3a576'),('6647105558','4396782047'),('8284602928','6027336854'),('/proc/5204','/proc/27414')]
    for old,new in pairs:raw=raw.replace(old,new)
    return raw


def sources():
    values={bind(n):bind(raw)for n,raw in prior.sources().items()}
    proved=current.sources()
    for suffix in ['parent_receipt.py','warning_parent_projection.py','configuration.py','configuration_capture.py','row_bound.py','stable_journal.py']:
        key='pg2890_'+suffix
        if key not in proved:raise ValueError('current original/schema/PID1 helper required')
        values['pg2942_'+suffix]=proved[key].replace('pg2890','pg2942').replace('Pg2890','Pg2942').replace('PG2890','PG2942')
    contract=values['pg2942_resume_contract.py']
    node=next(n for n in ast.parse(contract).body if isinstance(n,ast.FunctionDef)and n.name=='runtime_tree')
    contract=contract[:contract.index(ast.get_source_segment(contract,node))]
    contract+='ROOT=RUNTIME\n\n'+inspect.getsource(parent_contract.row)+'\n'+inspect.getsource(parent_contract.runtime_tree)
    values['pg2942_resume_contract.py']=contract
    values['pg2942_runtime_writer.py']+='\n'+inspect.getsource(parent_contract.owned_create_parent)
    refs=values['pg2942_native_refs.py']
    old="require(set(runtime_before)=={str(runtime_root),str(runtime_directory)}and not list(runtime_directory.iterdir()))\n    require(metadata(runtime_directory)[2:6]==[0,0,stat.S_IFDIR|0o755,2]and not os.listxattr(runtime_root)and not os.listxattr(runtime_directory))"
    new="""require(set(runtime_before)in [{str(runtime_root)},{str(runtime_root),str(runtime_directory)}]and not os.listxattr(runtime_root))
    if str(runtime_directory)in runtime_before:
        require(metadata(runtime_directory)[2:6]==[0,0,stat.S_IFDIR|0o755,2]and not list(runtime_directory.iterdir())and not os.listxattr(runtime_directory))
    else:
        require(metadata(runtime_root)[2:6]==[0,0,stat.S_IFDIR|0o755,2]and not list(runtime_root.iterdir()))"""
    if refs.count(old)!=1:raise ValueError('one actual empty-runtime admission boundary required')
    refs=refs.replace(old,new)
    old="            runtime.owned_prepare(runtime_before[str(runtime_directory)]['metadata'],dropin)"
    new="""            if str(runtime_directory)not in runtime_before:
                expected_parent=runtime.owned_create_parent(runtime_before[str(runtime_root)]['metadata'],runtime.UNIT,runtime.require,runtime.metadata,runtime.named_metadata)
                durable_save(SAVE,'runtime-parent-created.private.json',json.dumps({'rootBefore':runtime_before[str(runtime_root)],'newParentMetadata':expected_parent},sort_keys=True).encode())
            else:
                expected_parent=runtime_before[str(runtime_directory)]['metadata']
            runtime.owned_prepare(expected_parent,dropin)"""
    if refs.count(old)!=1:raise ValueError('one held original/no-parent writer boundary required')
    values['pg2942_native_refs.py']=refs.replace(old,new)
    # Bind the complete returned graph, not only its outer generator function.
    values={bind(n):bind(raw)for n,raw in values.items()}
    for name,raw in values.items():
        if name.endswith('.py'):
            if check(raw,'<whole completed current resume '+name+'>'):raise ValueError('complete source namespace required')
            compile(raw,'<new current completed resume>','exec')
        if any(x in raw for x in [prior.SOURCE,prior.BOM,prior.RUN,'PG2126','pg2304','b2d6f605']):
            raise ValueError('old positive authority in completed source: '+name)
    return values
