"""SSC259 cold empty runtime branch; SSC260 canonical name, SS343 fresh activation."""
import inspect
from pyflakes.api import check
import pg1160_runtime_writer as cold_writer
import pg2304_current_completed_resume_sources as prior

SOURCE=prior.SOURCE
BOM=prior.BOM
BEFORE=prior.BEFORE
RUN=prior.RUN
TOOLS='pg2316-current-cold-resume-tools-v1'
SAVE='pg2320-current-cold-resume-preparation-v1'
CLASS='Pg2316FreshResumePreparation'


def bind(raw):
    return raw.replace(prior.TOOLS,TOOLS).replace(prior.SAVE,SAVE).replace('pg2304','pg2316').replace('Pg2304','Pg2316').replace('PG2304','PG2316')


def sources():
    result={bind(name):bind(raw)for name,raw in prior.sources().items()}
    writer=inspect.getsource(cold_writer).replace("NAME='pg1160-once-resume.conf'","NAME='zz-pg2316-once-resume.conf'").replace("RUN_ID='343a5a1b-d064-47d5-88c2-31c36d7ba7a4'","RUN_ID="+repr(RUN)).replace('# SSC259: cold fixed same-active same-cutoff resume; retire after genuine terminal.','# SS343 6.13: explicit same-run fresh activation; retire after genuine terminal.')
    result['pg2316_runtime_writer.py']=writer
    refs=result['pg2316_native_refs.py']
    old="""    require(set(runtime_before)=={str(runtime_root),str(runtime_directory)}and not list(runtime_directory.iterdir()))
    require(metadata(runtime_directory)[2:6]==[0,0,stat.S_IFDIR|0o755,2]and not os.listxattr(runtime_root)and not os.listxattr(runtime_directory))"""
    new="""    require(set(runtime_before)=={str(runtime_root)}and not list(runtime_root.iterdir())and not os.path.lexists(runtime_directory))
    require(metadata(runtime_root)[2:6]==[0,0,stat.S_IFDIR|0o755,2]and not os.listxattr(runtime_root))
    require(command(['/usr/bin/findmnt','--target',str(runtime_root),'--output','FSTYPE','--noheadings']).strip()==b'tmpfs')"""
    refs=prior.one(refs,old,new)
    refs=prior.one(refs,'runtime.owned_prepare(runtime_before[str(runtime_directory)][\'metadata\'],dropin)','runtime.owned_prepare(runtime_before[str(runtime_root)][\'metadata\'],dropin)')
    result['pg2316_native_refs.py']=refs
    contract=result['pg2316_resume_contract.py']
    contract=contract[:contract.index('def runtime_tree(')]+COLD_TREE
    result['pg2316_resume_contract.py']=contract
    for name,raw in result.items():
        if name.endswith('.py'):
            if check(raw,'<current cold resume '+name+'>'):raise ValueError('whole cold source globals required')
            compile(raw,'<current cold resume>','exec')
    return result


COLD_TREE=r'''
def runtime_tree(before,actual,dropin,lower_ns,upper_ns):
    if type(before)is not dict or type(actual)is not dict or set(before)!={RUNTIME}or set(actual)!={RUNTIME,DIRECTORY,TARGET}:return False
    if type(dropin)is not bytes or not 0<len(dropin)<=4096 or type(lower_ns)is not int or type(upper_ns)is not int or not 0<=lower_ns<=upper_ns:return False
    for row in [before[RUNTIME],actual[RUNTIME],actual[DIRECTORY],actual[TARGET]]:
        if type(row)is not dict or set(row)!={'metadata','sha256'}or type(row['metadata'])is not list or len(row['metadata'])!=9 or any(type(v)is not int or v<0 for v in row['metadata']):return False
    old,new=before[RUNTIME]['metadata'],actual[RUNTIME]['metadata']
    if old[1]==0 or old[2:6]!=[0,0,stat.S_IFDIR|0o755,2]or new[:5]!=old[:5]or new[5]!=old[5]+1 or new[6]<old[6]:return False
    if before[RUNTIME]['sha256']is not None or actual[RUNTIME]['sha256']is not None:return False
    if any(not max(old[i],lower_ns)<=new[i]<=upper_ns for i in [7,8]):return False
    directory=actual[DIRECTORY]['metadata'];file=actual[TARGET]['metadata']
    if directory[0]!=old[0]or directory[1]in {0,old[1]}or directory[2:6]!=[0,0,stat.S_IFDIR|0o755,2]or actual[DIRECTORY]['sha256']is not None:return False
    if file[0]!=old[0]or file[1]in {0,old[1],directory[1]}or file[2:7]!=[0,0,stat.S_IFREG|0o644,1,len(dropin)]:return False
    if any(not lower_ns<=row[i]<=upper_ns for row in [directory,file]for i in [7,8]):return False
    return actual[TARGET]['sha256']==hashlib.sha256(dropin).hexdigest()
'''
