"""Batch full overload all-six physical/source proof; byte-only rows are not current PT."""
import copy
import datetime
import json
import os
from pathlib import Path
import subprocess
import pg8302_http_cdf_six_trace as base
import pg8900_batch_full_text_fixed_host as selected
from host_tool_invocation import capture,verify

host,architecture,steps=base.host,base.architecture,base.steps
SOURCE=selected.SOURCE
BEFORE='28befbf2cac86840b6adef53b6c5f972e6f9610f'
MAIN='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/BatchMetricText.java'
UNIT=MAIN.replace('/main/','/test/').replace('.java','Test.java')
SLOT=host.W/'pg8904-batch-full-text-fixed-trace-v1'
OUT=host.BASE/'PG8904-batch-full-text-fixed-trace-v1'

def protocol(text):
    body=''.join(text.split())
    assert 'publicStringscrape(MeterRegistrysource,Stringmode,BatchStandardMetricSourcestandard){Objects.requireNonNull(standard,"standardmetricowner");Stringcustom=scrape(source,mode);if("STANDARD".equals(mode))returncustom;returncustom+Objects.requireNonNull(standard.scrape(mode),"standardmetrictext");}' in body
    for denied in ('standard.bind(', 'standard.close(', 'newBatchStandardMetricSource(', 'java.net.', 'javax.sql.', 'catch('):
        assert denied not in body

def main():
    invocation=capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    pins={
      'normal':('PG8898-batch-full-text-fixed-six-compile-v1/manifest.json',selected.COMPILE_SHA),
      'post':('PG8902-batch-full-text-fixed-post-v1/manifest.json',host.sha(host.BASE/'PG8902-batch-full-text-fixed-post-v1/manifest.json')),
      'priorNormal':('PG8868-web-caller-metric-six-compile-v1/manifest.json','bf2a02c6a70f65d1bc002edafa02d4566f7aa8a8e5d1d1fc8d829e188492bc68'),
      'priorTrace':('PG8874-web-caller-metric-trace-v1/manifest.json','8dfa48d3a93ebd2a022c97d82e5292bede36bc08486ee4e5e99e9b5d06c5f428'),
      'original':('PG6930-current4222-cases/qualification.json','728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731'),
      'architecture':('PG6960-archunit-static-v1/manifest.json','7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f')}
    proof={}
    for key,(path,digest) in pins.items():
        assert host.sha(host.BASE/path)==digest
        proof[key]=json.loads((host.BASE/path).read_text())
    normal,current=proof['normal'],proof['post']
    assert normal['source']==current['source']==SOURCE and normal['actualExit']==normal['terminal']['actualExit']==current['actualExit']==normal['testsExecuted']==0
    assert current['tests']==36 and current['suites']==1 and len(current['executableClasses'])==1
    assert current['actualCrcMismatch']==0 and current['actualSessions']==1 and not current['coverageUnion'] and all(row['missed']==0 for row in current['counters'].values())
    assert current['unclassified']==0 and not current['classifiedPmdContext'] and current['suppressionsAdded'] is False
    assert proof['priorNormal']['source']==proof['priorTrace']['source']==BEFORE
    snapshot=selected.COMPILE/'snapshot';hashes=normal['begin']['inputHashes']
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in hashes.items())
    previous=base.inventory(proof['priorNormal']);physical=base.inventory(normal)
    changed={name:dict(beforeSha256=previous[name],sha256=digest) for name,digest in physical.items() if previous[name]!=digest}
    assert len(physical)==len(previous)==1834 and set(physical)==set(previous)
    assert set(changed)=={'batch:dev/codex/schubert/nk/batch/monitoring/BatchMetricText.class'}
    original=proof['original']['allPhysicalMainSha256']
    unchanged=sum(physical[name]==digest for name,digest in original.items())
    assert len(original)==1669 and unchanged==1665
    for name,digest in current['physicalClasses'].items(): assert physical['batch:'+name]==digest
    delta=set(subprocess.check_output(['git','diff','--name-only',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=host.ROOT,text=True).splitlines())
    assert delta=={MAIN,UNIT}
    rows=copy.deepcopy(proof['priorTrace']['sourceRows']);indexed={row['path']:row for row in rows}
    assert len(rows)==len(indexed)==229 and delta<=set(indexed)
    for path,row in indexed.items():
        assert host.sha(snapshot/path)==hashes[path]
        if path not in delta: assert row['sha256']==hashes[path]
        row.update(sha256=hashes[path],owner='WBS-P018-09',sharedReference='WBS-C07',sharedAdditionalCostPp=0,relationship='CURRENT_BATCH_FULL_SELECTED_PT' if path in delta else 'BYTE_ONLY_NOT_CURRENT_PT_QUALIFICATION')
    text=(snapshot/MAIN).read_text();protocol(text)
    begin=text.index('  /** 1833/PG-D624:')
    end=text.index('  /**\n   * STANDARD reads no detailed source;')
    old=subprocess.check_output(['git','show',BEFORE+':'+MAIN],cwd=host.ROOT,text=True)
    assert text[:begin]+text[end:]==old
    unit=(snapshot/UNIT).read_text();old_unit=subprocess.check_output(['git','show',BEFORE+':'+UNIT],cwd=host.ROOT,text=True)
    begin=unit.index('  private static final String FULL_STANDARD')
    assert unit[:begin].rstrip()+'\n}\n'==old_unit
    negatives=[]
    for name,changed_text in [('wrong-standard-mode',text.replace('"STANDARD".equals(mode)','"DEBUG".equals(mode)',1)),('dropped-standard-boundary',text.replace('Objects.requireNonNull(standard, "standard metric owner");','',1)),('dropped-text-boundary',text.replace('Objects.requireNonNull(standard.scrape(mode), "standard metric text")','standard.scrape(mode)',1)),('reversed-order',text.replace('String custom = scrape(source, mode);','String custom = standard.scrape(mode);',1)),('implicit-close',text.replace('String custom = scrape(source, mode);','standard.close();String custom = scrape(source, mode);',1))]:
        assert changed_text!=text
        try: protocol(changed_text)
        except AssertionError: negatives.append(name)
        else: raise AssertionError('every borrowed-output mutation rejects')
    assert host.sha(architecture.SOURCE)==proof['architecture']['toolSourceSha256'] and host.sha(architecture.ARCH)==architecture.ARCH_SHA and host.sha(architecture.SLF)==architecture.SLF_SHA
    SLOT.mkdir();steps.SLOT=SLOT
    classes=SLOT/'reader';classes.mkdir()
    compiled,_=steps.step('architecture-compile',[str(architecture.JAVAC),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',os.pathsep.join([str(architecture.ARCH),str(architecture.SLF)]),'-d',str(classes),str(architecture.SOURCE)])
    assert compiled['actualExit']==0
    checked,output=steps.step('architecture-six',[str(architecture.JAVA),'-cp',os.pathsep.join([str(classes),str(architecture.ARCH),str(architecture.SLF)]),'ModuleDependencyAudit',*[role+'='+normal['jars'][role]['path'] for role in architecture.MODULES]])
    analysis=architecture.parse(output)
    assert checked['actualExit']==0 and analysis['physical']==1834 and not analysis['findings'] and len(analysis['rules'])==5 and all(value==0 for value in analysis['rules'].values())
    assert all(host.sha(snapshot/path)==host.sha(host.ROOT/path)==digest for path,digest in hashes.items())
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,source=SOURCE,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),invocation=invocation,witnesses=pins,physicalClasses=physical,allPhysicalClassCount=1834,physicalChanged=changed,previousPhysicalUnchanged=1833,originalPhysicalUnchanged=unchanged,sourceRows=rows,sourceCount=229,currentTests=36,currentSuites=1,newTests=12,necessaryModifiedSourceRegression=24,currentCounters=current['counters'],protocolNegatives=negatives,oldOverloadAnd24TestBodiesUnchanged=True,architecture=dict(result=analysis,compileReceipt=compiled,receipt=checked,targetInitialized=False),productTestsExecutedByPost=0,coverageUnion=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0)
    host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,physical=1834,sourceOwners=229,protocolNegatives=len(negatives),manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':
    main()
