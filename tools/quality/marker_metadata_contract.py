"""Retain only proved empty interfaces as metadata, never exclude executable bytecode."""
import hashlib
from pathlib import Path
import re
import subprocess

def validate_description(description,reason):
    if not isinstance(reason,str) or not reason.strip():
        raise ValueError('explicit metadata reason required')
    flags=re.search(r'^\s*flags: \(0x[0-9a-fA-F]+\) (.+)$',description,re.M)
    shape=re.search(r'^\s*interfaces: (\d+), fields: (\d+), methods: (\d+), attributes: (\d+)\s*$',description,re.M)
    if not flags or set(flags[1].split(', '))!={'ACC_INTERFACE','ACC_ABSTRACT'} or not shape or shape.group(1,2,3)!=('0','0','0'):
        raise ValueError('only package-local empty interface with no fields/methods/initialization')

def verify_markers(classes,javap,declared):
    rows=[]
    for name,reason in declared.items():
        if not re.fullmatch(r'[a-zA-Z0-9_/]+\.class',name) or name.startswith('/'):
            raise ValueError('relative classfile name required')
        file=Path(classes)/name
        done=subprocess.run([str(javap),'-verbose',str(file)],capture_output=True,text=True,check=False)
        if done.returncode:raise ValueError('noninitializing metadata inspection failed')
        validate_description(done.stdout,reason)
        rows.append(dict(className=name,sha256=hashlib.sha256(file.read_bytes()).hexdigest(),reason=reason,
            fields=0,methods=0,initializationMethods=0,targetInitialized=False,actualExit=done.returncode,
            command=[str(javap),'-verbose',str(file)]))
    return rows
