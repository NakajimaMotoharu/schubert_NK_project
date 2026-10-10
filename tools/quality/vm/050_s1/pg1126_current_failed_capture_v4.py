"""New-only current failed capture with real full-held metadata projection."""
import ast
import inspect
from pathlib import Path
import pg1120_current_failed_capture as transport
from pg1124_current_failed_capture_v3 import payload as previous

R=Path(__file__).resolve().parent


def payload():
    raw=previous().replace('failed-capture-v3','failed-capture-v4')
    marker="original={name[len(current_path):].lstrip('/'):entry for name,entry in before['trees']['/opt/schubert-nk'].items()if name==current_path or name.startswith(current_path+'/')}"
    if raw.count(marker)!=1:raise ValueError('fixed real-shaped held inventory insertion refused')
    raw=raw.replace(marker,'pass # full projection follows current observation; direct tree remains finite.')
    marker="now={name[len(current_path):].lstrip('/'):entry for name,entry in tree(pathlib.Path(current_path)).items()}"
    if raw.count(marker)!=1:raise ValueError('fixed current source tree observation refused')
    extra=r'''
 ancestor_paths=['/','/opt','/opt/schubert-nk','/opt/schubert-nk/releases']
 ancestor_names=['/','opt','schubert-nk','releases']
 ancestors=[{'name':name,'value':entry(pathlib.Path(path))}for name,path in zip(ancestor_names,ancestor_paths)]
 require(len(before['heldWholeMetadata'])==7)
 original=held.project(before['heldWholeMetadata'][1],now,ancestors,'0.1.0-PG1068')
'''
    raw=raw.replace(marker,marker+'\n'+extra)
    oracle=(R/'pg1125_held_current_projection.py').read_text()
    raw="import types\nheld=types.ModuleType('independent_held_current');exec("+repr(oracle)+",held.__dict__)\n"+raw
    ast.parse(raw);return raw


def main():
    raw=inspect.getsource(transport.main)
    raw=raw.replace('pg1120-current-failed-capture-v1','pg1126-current-failed-capture-v4')
    raw=raw.replace('PG1120-current-failed-capture-v1','PG1126-current-failed-capture-v4')
    env=dict(transport.__dict__);env['PAYLOAD']=payload()
    exec(compile(raw,'<new-only real held-current failed capture>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
