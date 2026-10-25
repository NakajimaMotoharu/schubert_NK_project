"""Classify two legacy rows without execution, suppression or treating diagnosis as static PASS."""
from collections import Counter
import copy
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile
import pg8302_http_cdf_six_trace as base
from host_tool_invocation import capture, verify

host=base.host
SOURCE='3641d0f49e6b33fe64de718703f134406dfddb30'
OUT=host.BASE/'PG9224-api-life-legacy-contract-v1'
MAIN='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime.java'
SS='documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md'
FORMAL='8b91944df5820535e23ba2469740f1c0aa94c447'

def contract(rows,text):
    assert Counter(row['rule'] for row in rows)==Counter(AvoidUsingVolatile=1,EmptyCatchBlock=1)
    assert 'private volatile boolean installed;' in text and 'installed = true;' in text
    assert 'if (installed) {' in text and 'installed = false;' in text
    assert 'catch (IllegalStateException shutdownInProgress)' in text
    assert re.search(r'catch \(IllegalStateException shutdownInProgress\) \{\s*//[^\n]*\n\s*\}',text)
    assert 'finally {\n      finished.countDown();' in text
    assert 'Runtime.getRuntime().removeShutdownHook(hook);' in text
    assert not re.search(r'catch \((RuntimeException|Exception|Throwable)\b',text)

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists()
    pins={
      'normal':('PG9210-api-factory-debug-six-compile-v1/manifest.json','80b8d4f5f4e16723b5871771fcd3bd03bd068e2a59d17cbf1e8d6e8486f3a39b'),
      'partial':('PG9185-api-lifetime-budget-partial-review-v1/manifest.json','d64eddc17653bac1849b8c653f9eee1f822a25fe5f7befc59ebe331d17c326f1'),
      'raw':('PG9183-api-lifetime-budget-static-v1/manifest.json','9da454967ec0eb9f036dab2b05f73ff29399eb211ee4652b5bbb1a29eb6f6c8f')}
    proof={}
    for key,(path,digest) in pins.items():
        assert host.sha(host.BASE/path)==digest; proof[key]=json.loads((host.BASE/path).read_bytes())
    normal,partial,raw=proof['normal'],proof['partial'],proof['raw']
    assert normal['source']==SOURCE and normal['actualExit']==0
    text=(host.ROOT/MAIN).read_text(); digest=host.sha(host.ROOT/MAIN)
    assert digest==normal['begin']['inputHashes'][MAIN]==raw['sourceHashes'][MAIN]
    rows=[row['raw'] for row in partial['unresolvedStaticRows']]
    contract(rows,text); assert len(partial['staticDispositions'])==7
    all_rows=[*rows,*[row['raw'] for row in partial['staticDispositions']]]
    canonical=lambda values:Counter(json.dumps(v,sort_keys=True) for v in values)
    assert canonical(all_rows)==canonical(raw['static']['pmd']['rawFindings'])
    assert raw['static']['pmd']['receipt']['actualExit']==4 and raw['static']['pmd']['findings']==9
    vendor=host.TC/'static-gates-20261015/pmd-bin-7.28.0/lib/pmd-java-7.28.0.jar'
    assert host.sha(vendor)=='068b2b5fb276559c32d52e3675d297a458bf27fe181b675cee10555a55c131bd'
    with zipfile.ZipFile(vendor) as archive:
        rule={}
        for path in ('category/java/multithreading.xml','category/java/errorprone.xml'):
            for node in ET.fromstring(archive.read(path)).findall('{*}rule'):
                if node.get('name') in ('AvoidUsingVolatile','EmptyCatchBlock'):
                    rule[node.get('name')]=' '.join(''.join(node.itertext()).split())
    assert 'allows no exceptions' in rule['AvoidUsingVolatile'] and 'AtomicBoolean' in rule['AvoidUsingVolatile']
    assert 'allowCommentedBlocks' in rule['EmptyCatchBlock']
    assert subprocess.check_output(['git','show',FORMAL+':'+SS],cwd=host.ROOT)==(host.ROOT/SS).read_bytes()
    javap=host.TC/'jdk-25.0.4/bin/javap'; commands={}
    for kind in ('Runtime','ApplicationShutdownHooks'):
        command=[str(javap),'-c','-p','java.lang.'+kind]
        observed=subprocess.run(command,capture_output=True,text=True,check=False,timeout=30)
        assert observed.returncode==0
        commands[kind]=dict(command=command,actualExit=observed.returncode,bytecode=observed.stdout)
    runtime=commands['Runtime']['bytecode']; hooks=commands['ApplicationShutdownHooks']['bytecode']
    segment=runtime[runtime.index('public boolean removeShutdownHook'):runtime.index('public void halt')]
    assert 'ApplicationShutdownHooks.remove' in segment
    remove=hooks[hooks.index('static synchronized boolean remove'):hooks.index('static void runHooks')]
    assert 'getstatic' in remove and 'Field hooks:' in remove and 'ifnonnull' in remove
    assert 'java/lang/IllegalStateException' in remove and 'Shutdown in progress' in remove
    rejected=[]
    for name,source,items in (
      ('broad-catch',text.replace('catch (IllegalStateException shutdownInProgress)','catch (RuntimeException shutdownInProgress)'),rows),
      ('missing-final-notify',text.replace('finished.countDown();',''),rows),
      ('unknown-row',text,[dict(rows[0],rule='UNKNOWN'),rows[1]]),
      ('old-state-invented',text.replace('private volatile boolean installed;','private boolean installed;'),rows)):
        try: contract(copy.deepcopy(items),source)
        except (AssertionError,ValueError,KeyError): rejected.append(name)
        else: raise AssertionError('unknown contract accepted')
    verify(invocation); OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
      invocation=invocation,witnesses=pins,sourcePath=MAIN,sourceSha256=digest,formalDesignSource=FORMAL,
      formalDesignSha256=host.sha(host.ROOT/SS),vendorSha256=host.sha(vendor),
      jdkModulesSha256=host.sha(host.TC/'jdk-25.0.4/lib/modules'),javapSha256=host.sha(javap),jdkReadOnlyBytecode=commands,
      examinedRows=rows,existing7ReviewUnchanged=True,unclassified=0,applicableUnresolved=2,
      conclusions=[
        dict(rule='AvoidUsingVolatile',decision='APPLICABLE_REQUIRES_ATOMIC_OWNER_STATE_NOT_SUPPRESSION',
          reason='Pinned vendor explicitly has no exceptions; scalar visibility does not justify violating current zero-applicable-violation gate. AtomicBoolean getAndSet provides explicit single release claim.'),
        dict(rule='EmptyCatchBlock',decision='KNOWN_JDK_SHUTDOWN_TRANSITION_BUT_RAW_STYLE_REMEDIATION_REQUIRED',
          reason='JDK compiled remove throws ISE during shutdown; finally already notifies held owner. Preserve catch type and finally, express explicit terminal control flow, not ignore-name/comment suppression.')],
      proposedInternalFix='AtomicBoolean installed; set(true) after existing install; getAndSet(false) before remove; catch returns through unchanged finally',
      metadataCounterexamples=rejected,rawPmd=9,rawPmdExit=4,rawStaticExit=1,
      codeChanged=False,productTestsExecuted=0,coverage=None,currentSourcePtTransferred=False,
      hookOperationsExecuted=0,ptExecutionExempt=False,wholeClassStaticAccepted=False,programPtComplete=False,
      whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None))
    print(json.dumps(dict(actualExit=0,examinedRows=2,applicableUnresolved=2,productTests=0,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
