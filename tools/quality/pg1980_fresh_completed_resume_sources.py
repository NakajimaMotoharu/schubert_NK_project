"""Fresh completed-run resume setup only, same owner/scopes; no business start or permits."""
import inspect
import pg1925_disjoint_role_partial_reload_sources as prior
import pg1981_fresh_resume_contract as contract
from pg1172_existing_runtime_writer import source as existing_writer
from pg1877_warning_publication_sources import once

TOOLS='pg1980-fresh-resume-tools-v1'
SAVE='pg1984-fresh-resume-preparation-v1'
CLASS='Pg1980FreshResumePreparation'
BOM=prior.BOM
BEFORE='ee13ec0b75e1320f4daba711ef90d24b2c05ae588c3b27fedb0224114896fc15'


def bind(raw):
    return raw.replace(prior.TOOLS,TOOLS).replace(prior.SAVE,SAVE).replace(prior.CLASS,CLASS).replace('pg1925','pg1980').replace('Pg1925','Pg1980').replace('PG1925','PG1980').replace('finish-reload','prepare-resume').replace(prior.BEFORE,BEFORE).replace('pg1904-partial-recovery-closed-post-v1','pg1963-reload-ref-scoped-full-post-v1')


def sources():
    result={bind(n):bind(r)for n,r in prior.sources().items()}
    key='pg1980_native_refs.py';raw=result[key]
    raw=once(raw,'import pg1980_existing_unit as unit_io','import pg1980_runtime_writer as runtime\nimport pg1980_resume_contract as resume_contract')
    raw=once(raw,"'SuccessExitStatus': '10'if placed else''","'SuccessExitStatus': '10'")
    raw=once(raw,'    existing_unit=unit_io.ExistingUnit(SAVE)',SETUP)
    start=raw.index('        for u, v in cfg.items():');end=raw.index('        durable =',start)
    raw=raw[:start]+CONFIGURATION+raw[end:]
    raw=once(raw,'        require(first is not None and same_value(now, first))',CHECK_DATA)
    raw=once(raw,"        if action == 'reload':","        if action == 'prepare':")
    raw=once(raw,'            existing_unit.reload()',PREPARE)
    raw=once(raw,"        check_data(capture_data(action != 'release'))","        check_data(capture_data(action != 'release'))")
    raw=once(raw,'            existing_unit.close();bus.close()','            bus.close()')
    result[key]=raw
    stop='pg1980_native_owned_stop.py';result[stop]=result[stop].replace("'reload'","'prepare'")
    j=result[CLASS+'.java']
    j=once(j,'"reload".equals(name)','"prepare".equals(name)')
    j=once(j,'phase="ONLY_NORMAL_RELOAD";refs.check("reload");','phase="FINITE_FRESH_RESUME_PREPARATION";refs.check("prepare");')
    j=j.replace('partialExistingUnitVerified=true\\nnormalSingleReload=true','freshResumeRuntimePrepared=true\\nnormalSingleRuntimeReload=true')
    result[CLASS+'.java']=j
    del result['pg1980_existing_unit.py']
    writer=existing_writer().replace("NAME='zz-pg1160-once-resume.conf'","NAME="+repr(contract.NAME)).replace("RUN_ID='343a5a1b-d064-47d5-88c2-31c36d7ba7a4'","RUN_ID="+repr(contract.RUN))
    writer=once(writer,'# SSC259: cold fixed same-active same-cutoff resume; retire after genuine terminal.','# SS343 6.13: explicit same-run fresh activation; retire after genuine terminal.')
    result['pg1980_runtime_writer.py']=writer
    result['pg1980_resume_contract.py']=inspect.getsource(contract)
    for name,value in result.items():
        if name.endswith('.py'):compile(value,'<actual freshresume '+name+'>','exec')
    return result


SETUP=r'''
    runtime_root=pathlib.Path(resume_contract.RUNTIME);runtime_directory=pathlib.Path(resume_contract.DIRECTORY)
    runtime_before=tree(runtime_root)
    require(set(runtime_before)=={str(runtime_root),str(runtime_directory)}and not list(runtime_directory.iterdir()))
    require(metadata(runtime_directory)[2:6]==[0,0,stat.S_IFDIR|0o755,2]and not os.listxattr(runtime_root)and not os.listxattr(runtime_directory))
    require(runtime.NAME==resume_contract.NAME and runtime.RUN_ID==resume_contract.RUN)
    dropin=runtime.fixed_dropin(pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1846/systemd/schubert-nk-morning-controller.service').read_bytes(),pathlib.Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/pg477-native-coverage.conf').read_bytes())
    mutation_begin_ns=0;prepared_runtime=None
'''

CONFIGURATION=r'''
        if placed:
            require(resume_contract.configuration(signed_cfg,cfg,exec_record,config_same))
        else:
            for u,v in cfg.items():require(config_same(signed_cfg[u],v,exec_record))
'''

CHECK_DATA=r'''
        require(first is not None and set(now)==set(first))
        if not placed:require(same_value(now,first))
        else:
            require(all(same_value(now[k],first[k])for k in first if k not in {'configuration','runtime'}))
            require(resume_contract.configuration(first['configuration'],now['configuration'],exec_record,config_same))
            require(prepared_runtime is not None and now['runtime']==prepared_runtime)
            require(resume_contract.runtime_tree(first['runtime'],now['runtime'],dropin,mutation_begin_ns,time.time_ns()))
'''

PREPARE=r'''
            require(not placed and prepared_runtime is None and first is not None)
            mutation_begin_ns=time.time_ns()
            runtime.owned_prepare(runtime_before[str(runtime_directory)]['metadata'],dropin)
            prepared_runtime=tree(runtime_root)
            require(resume_contract.runtime_tree(first['runtime'],prepared_runtime,dropin,mutation_begin_ns,time.time_ns()))
            durable_save(SAVE,'new-runtime.private',dropin)
            durable_save(SAVE,'runtime-prepared.private.json',json.dumps(prepared_runtime,sort_keys=True).encode())
            durable_save(SAVE,'daemon-reload-reserved.private',b'one normal runtime daemon-reload; no retry\n')
            command(['/usr/bin/systemctl','daemon-reload'])
'''
