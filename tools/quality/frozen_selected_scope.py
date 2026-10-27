"""Metadata-only facts for selected Test changes; never an execution or access permission.

Module names do not imply Java packages: bootstrap also contains api packages.
Callers still pin manifests, verify actual bytes and review operations before any execution.
"""
import re

ROLES=frozenset(('api','batch','bootstrap','protocol','storage','web'))

def _hex(value,length):
    return isinstance(value,str) and re.fullmatch('[0-9a-f]{'+str(length)+'}',value) is not None

def derive_facts(plan,normal,source):
    if not _hex(source,40) or not isinstance(normal,dict) or not isinstance(plan,dict):
        raise ValueError('explicit fixed source and manifest objects required')
    if normal.get('source')!=source or type(normal.get('actualExit')) is not int or normal['actualExit']!=0 or type(normal.get('testsExecuted')) is not int or normal['testsExecuted']!=0:
        raise ValueError('successful normal build with PT0 on the fixed source required')
    begin=normal.get('begin');jars=normal.get('jars');changes=plan.get('sourceChanges')
    if not isinstance(begin,dict) or not isinstance(begin.get('inputHashes'),dict) or not isinstance(jars,dict) or set(jars)!=ROLES or not isinstance(changes,list) or not changes:
        raise ValueError('six-role build and nonempty explicit source changes required')
    all_jars={}
    for role in sorted(ROLES):
        info=jars[role]
        if not isinstance(info,dict) or set(info)!= {'path','sha256'} or not isinstance(info.get('path'),str) or not info['path'].endswith('.jar') or not _hex(info.get('sha256'),64):
            raise ValueError('one frozen path/hash per module JAR required')
        all_jars[role]=dict(path=info['path'],sha256=info['sha256'])
    paths=[r['path'] for r in all_jars.values()]
    if len(set(paths))!=len(paths):raise ValueError('module JAR aliases are not permitted')
    selected={};modules=set()
    for row in changes:
        if not isinstance(row,dict) or not isinstance(row.get('path'),str) or not _hex(row.get('sha256'),64):
            raise ValueError('explicit selected source path/hash required')
        path=row['path'];parts=path.split('/')
        if len(parts)<7 or any(p in ('','.','..') for p in parts) or any(ord(c)<32 or c in '\\:' for c in path) or parts[0]!='src' or not parts[1].startswith('schubert-nk-') or parts[2:5]!=['src','test','java'] or not path.endswith('.java'):
            raise ValueError('canonical repository-relative Test Java path required')
        role=parts[1].removeprefix('schubert-nk-')
        if role not in ROLES or path in selected or begin['inputHashes'].get(path)!=row['sha256']:
            raise ValueError('unique exact Test input and module required')
        selected[path]=row['sha256'];modules.add(role)
    return dict(source=source,sources=dict(sorted(selected.items())),modules=sorted(modules),allMainJars=all_jars,
        requiredModuleJars={role:dict(all_jars[role]) for role in sorted(modules)},mainJarPaths=paths,
        javaPackagePrefixes=None,metadataOnly=True,executionPermission=False)

def require_classpath(facts,entries):
    if not isinstance(facts,dict) or facts.get('metadataOnly') is not True or facts.get('executionPermission') is not False or not isinstance(facts.get('mainJarPaths'),list):
        raise ValueError('metadata facts, not an execution permission, required')
    required=facts['mainJarPaths']
    if len(required)!=6 or any(not isinstance(p,str) or not p for p in required) or len(set(required))!=6:
        raise ValueError('six distinct frozen module JARs required')
    if not isinstance(entries,list) or not entries or any(not isinstance(p,str) or not p for p in entries) or len(set(entries))!=len(entries) or not set(required)<=set(entries):
        raise ValueError('unique classpath with all frozen Main JARs required')
    return tuple(entries)
