"""BUG1265: existing-parent-only complete graph; never cold-create or replace the parent."""
import ast
import inspect
import json
from pyflakes.api import check
import pg3060_browser_resume_sources as previous
import pg2304_current_completed_resume_sources as normal
from pg3066_browser_resume_post import existing_parent_metadata
from pg1446_current_cold_stage import W

SOURCE, BOM, BOOT, RUN, BEFORE = previous.SOURCE, previous.BOM, previous.BOOT, previous.RUN, previous.BEFORE
TOOLS = 'pg3080-retained-parent-resume-tools-v1'
SAVE = 'pg3084-retained-parent-resume-preparation-v1'
CLASS = 'Pg3080FreshResumePreparation'


def bind(raw):
    return raw.replace(previous.TOOLS, TOOLS).replace(previous.SAVE, SAVE).replace('pg3060', 'pg3080').replace('Pg3060', 'Pg3080').replace('PG3060', 'PG3080')


def admit_existing_runtime(before, root, directory, metadata, acl):
    if set(before) != {str(root), str(directory)} or list(directory.iterdir()) or acl(root) or acl(directory):
        raise ValueError('exact original empty parent required')
    for path, links in [(root, 3), (directory, 2)]:
        current = metadata(path)
        if current != before[str(path)]['metadata'] or current[2:6] != [0, 0, 0o40755, links] or before[str(path)]['sha256'] is not None:
            raise ValueError('retained runtime parent identity changed')


TREE = r'''
def runtime_tree(before,actual,dropin,lower_ns,upper_ns):
    if type(before)is not dict or type(actual)is not dict or type(dropin)is not bytes or not 0<len(dropin)<=4096:return False
    try:
        for row in list(before.values())+list(actual.values()):
            if type(row)is not dict or set(row)!={'metadata','sha256'}or type(row['metadata'])is not list or len(row['metadata'])!=9 or any(type(v)is not int or v<0 for v in row['metadata']):return False
        existing_parent_metadata(before,actual,RUNTIME,DIRECTORY,TARGET,lower_ns,upper_ns,dropin)
        return all(v[p]['sha256']is None for v in [before,actual]for p in [RUNTIME,DIRECTORY])and actual[TARGET]['sha256']==hashlib.sha256(dropin).hexdigest()
    except (ValueError,TypeError,KeyError,IndexError):return False
'''


def sources():
    post = json.loads((W / 'pg3078-recovered-browser-full-post-v1/manifest.safe.json').read_bytes())
    if not (post['actualExit'] == 0 and post['allClientAdvisoryFlock0'] and post['proofHashes']['after.private.json']['sha256'] == BEFORE):
        raise ValueError('actual whole post after current unknown recovery required')
    values = {bind(n): bind(raw) for n, raw in previous.sources().items()}
    writer = normal.sources()['pg2304_runtime_writer.py'].replace('zz-pg2304-once-resume.conf', 'zz-pg3080-once-resume.conf').replace("RUN_ID='91f5484b-9702-4c7c-97f3-dd5110a853f9'", 'RUN_ID=' + repr(RUN))
    values['pg3080_runtime_writer.py'] = writer
    refs = values['pg3080_native_refs.py']
    old = "    require(set(runtime_before)=={str(runtime_root)}and not list(runtime_root.iterdir())and not os.path.lexists(runtime_directory))\n    require(metadata(runtime_root)[2:6]==[0,0,stat.S_IFDIR|0o755,2]and not os.listxattr(runtime_root))"
    if refs.count(old) != 1:
        raise ValueError('one proven failed cold-only input admission required')
    refs = refs.replace(old, '    admit_existing_runtime(runtime_before,runtime_root,runtime_directory,metadata,os.listxattr)')
    old = "runtime.owned_prepare(runtime_before[str(runtime_root)]['metadata'],dropin)"
    if refs.count(old) != 1:
        raise ValueError('one actual held-parent writer call required')
    refs = refs.replace(old, "runtime.owned_prepare(runtime_before[str(runtime_directory)]['metadata'],dropin)")
    refs = refs.replace('def main():', inspect.getsource(admit_existing_runtime) + '\ndef main():', 1)
    values['pg3080_native_refs.py'] = refs
    contract = values['pg3080_resume_contract.py']
    node = next(n for n in ast.parse(contract).body if isinstance(n, ast.FunctionDef) and n.name == 'runtime_tree')
    contract = contract.replace(ast.get_source_segment(contract, node), inspect.getsource(existing_parent_metadata) + '\n' + TREE)
    contract = contract.replace('import stat\n', '')
    values['pg3080_resume_contract.py'] = contract
    for name, raw in values.items():
        if name.endswith('.py'):
            if check(raw, '<complete retained-parent source ' + name + '>'):
                raise ValueError('complete returned graph globals required')
            compile(raw, '<retained original parent only>', 'exec')
    return values
