"""SSC283 finite WARNING publication plus sole Unit/reload under one owner."""
import inspect
import pg1306_ordinary_publication_sources as template
from pg1872_warning_ro_marker_sources import sources as ro_sources
from pg1844_warning_unit_full_six import CANDIDATE,OLD
import pg1877_unit_exchange_contract as unit_contract

TOOLS='pg1877-warning-publication-tools-v1'
SAVE='pg1881-warning-publication-v1'
CLASS='Pg1877OrdinaryPublication'
BOM='ee75d0cd61457462eca59e67f5af2d8e677427071514940f3fb594ba93a026d7'
BEFORE='1928d1bd0d8aa0f00d3b1e4bb120e78c0bc710a9d5a219d89b3853d4929a11d6'


def once(raw,old,new):
    if raw.count(old)!=1:raise ValueError('one actual SSC283 source boundary required: '+old[:60])
    return raw.replace(old,new)


def cohort(raw):
    changes=[('PG1068','PG1638'),('pg1068','pg1638'),('PG1292','PG1846'),('pg1292','pg1846'),('d5b00104280028d9ea81b44c1d1c805f3c2861ed',OLD),('769ddb15cd735c25fef581b5f9850ef9d0053c0f',CANDIDATE),('0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d','195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1'),('ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99',BOM),('cbca8738-3b24-4090-b77c-bf029677cdd6','3d69f5af-6bac-46b1-a540-7591c4a79a0d'),('9f651096-aef9-4fba-90b0-a653e99f035a','4148e3e8-f107-431a-ab27-d6e6d1f1772e'),('27accac0-c118-4c98-9244-02625a2d88a7','9adbf05a-61d0-408b-b51d-ab19c7e5b16a'),('2026-10-10T20:03:22.718197Z','2026-10-12T18:20:32.598894Z'),('2026-10-10T20:22:34.439375Z','2026-10-12T18:46:52.677350Z'),('pg1304','pg1877'),('pg1305','pg1878'),('Pg1306','Pg1877'),('pg1306','pg1877'),('PG1306','PG1877')]
    for old,new in changes:raw=raw.replace(old,new)
    return raw


def sources():
    code=inspect.getsource(template.sources)
    for old,new in [('Pg1300','Pg1872'),('pg1300','pg1872'),('PG1300','PG1872'),('Pg1306','Pg1877'),('pg1306','pg1877'),('PG1306','PG1877')]:code=code.replace(old,new)
    code=once(code,"'/opt/schubert-nk/releases/0.1.0-PG1068' and owner() == held)","'/opt/schubert-nk/releases/0.1.0-PG1638' and owner() == held)")
    initial=cohort(template.REF_INITIAL).replace('direct_tree,fd_record,path_record','direct_tree,fd_record')
    initial=initial.replace('pg1253-native-stop-v1/after.private.json','pg1874-warning-candidate-host-ro-v1/after.private.json')
    initial=once(initial,"    begin_ns=time.time_ns();held_fds={};new_fds={}","    begin_ns=time.time_ns();held_fds={};new_fds={}\n    unit_exchange=unit_io.UnitExchange(SAVE);unit_phase='before'")
    initial=once(initial,"        require(first is not None and same_value({k:v for k,v in now.items()if k!='startup'},{k:v for k,v in first.items()if k!='startup'}))","        require(first is not None)\n        compared={k:v for k,v in now.items()if k!='startup'}\n        expected={k:v for k,v in first.items()if k!='startup'}\n        if unit_phase!='before':\n            unit_exchange.verify()\n            compared['unitFilesActual']=dict(compared['unitFilesActual'])\n            compared['unitFilesActual'][unit_io.PATH]=expected['unitFilesActual'][unit_io.PATH]\n        require(same_value(compared,expected))")
    loop=cohort(template.REF_LOOP)
    loop=once(loop,"        check_data(capture_data(action!='release'))","        if action=='unit':\n            require(publication_phase=='old-linked-private'and unit_phase=='before')\n            unit_exchange.exchange();unit_phase='exchanged'\n        elif action=='reload':\n            require(publication_phase=='old-linked-private'and unit_phase=='exchanged')\n            unit_exchange.reload();unit_phase='reloaded'\n        if action in ['terminal','release']:require(unit_phase=='reloaded')\n        check_data(capture_data(action!='release'))")
    loop=once(loop,"            os.close(save_fd)","            unit_exchange.close();os.close(save_fd)")
    java=cohort(template.JAVA_PUBLICATION).replace('Outcome.SUCCESS','Outcome.WARNING')
    java=once(java,'      phase="PUBLICATION_DIRECTORY_NORMAL_CLOSE";directory.close();','      phase="REGULAR_MORNING_UNIT_EXCHANGE";refs.check("unit");\n      phase="NORMAL_DAEMON_RELOAD";refs.check("reload");\n      phase="PUBLICATION_DIRECTORY_NORMAL_CLOSE";directory.close();')
    ns={**template.__dict__,'previous':lambda:ro_sources(BOM,BEFORE),'JAVA_PUBLICATION':java,'REF_INITIAL':initial,'REF_LOOP':loop,'TRANSITION_TEST':cohort(template.TRANSITION_TEST).replace('Outcome.SUCCESS','Outcome.__OLD__').replace('Outcome.WARNING','Outcome.SUCCESS').replace('Outcome.__OLD__','Outcome.WARNING')}
    exec(compile(code,'<actual WARNING publication composition>','exec'),ns)
    result={}
    for name,raw in ns['sources']().items():
        name=cohort(name);raw=cohort(raw)
        raw=raw.replace('pg1877-warning-candidate-ro-tools-v1',TOOLS).replace('pg1874-warning-candidate-host-ro-v1',SAVE)
        raw=raw.replace(SAVE+'/after.private.json','pg1874-warning-candidate-host-ro-v1/after.private.json')
        if name==CLASS+'.java':
            raw=raw.replace('"exchange","terminal"','"exchange","unit","reload","terminal"')
            raw=raw.replace('startsStopsReloadsEpochWrites0=true','startsStopsSqlWrites0=true\\ncanonicalEpochApprovalCurrentChanged=true\\nsoleUnitExchangedAndReloaded=true')
        elif name=='pg1877_native_owned_stop.py':raw=raw.replace("'exchange','terminal','release'","'exchange','unit','reload','terminal','release'").replace("action in ['terminal','release']and state=='old-linked-private'","action in ['unit','reload','terminal','release']and state=='old-linked-private'")
        elif name=='pg1877_native_refs.py':
            raw='import pg1877_unit_exchange_contract as unit_io\n'+raw
            raw=once(raw,"'SuccessExitStatus': ''","'SuccessExitStatus': '10'if unit_phase=='reloaded'else''")
        elif name=='pg1877_input_preflight.py':
            raw=raw.replace('Pg1877CandidateRo','Pg1877OrdinaryPublication')
            raw=raw.replace("'traceback'))","'traceback', 'uuid'))")
        if name.endswith('.py'):compile(raw,'<whole actual SSC283 Python>','exec')
        result[name]=raw
    result['pg1877_unit_exchange_contract.py']=inspect.getsource(unit_contract)
    return result
