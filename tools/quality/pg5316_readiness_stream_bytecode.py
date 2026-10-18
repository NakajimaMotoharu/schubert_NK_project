"""Actual3 stream boundaries, nullable raw-positive path and unchanged physical cohort."""
import subprocess
import xml.etree.ElementTree as ET
import pg5138_factory_bytecode as bytecode
import pg5265_owned_factory_proof as proof
import pg5314_readiness_stream_selected as entry

SOURCE='2a48e4e1b3fc5f90d35f7b8a9ce049947402f1df'
OUT='PG5316-readiness-stream-bytecode-v1'


def main():
    run,value=proof.prove(entry=entry,run_name='pg5314-readiness-stream-green-v1',
        prior_name='pg5304-permit-intent-green-v1',source=SOURCE,tests=1068,suites=129,
        package='dev.codex.schubert.nk.batch.platform.',
        scopes={'MorningCaddyReadiness':1,'MorningCaddyReadiness$NativeIo':0,'MorningServiceReadiness$NativeIo':2},
        kinds={'MorningCaddyReadiness':{},'MorningCaddyReadiness$NativeIo':{},
            'MorningServiceReadiness$NativeIo':{'Files.newInputStream:':1}},out_name=OUT)
    package='dev.codex.schubert.nk.batch.platform.'
    methods,hashed=bytecode.decode(run/'source','batch',package+'MorningCaddyReadiness')
    factory=bytecode.one([m for m in methods if any('ResourceScope$Acquire.open:' in o[2] for o in m['ops'])],'one nullable adapter factory')
    index=bytecode.index_of(factory,'ResourceScope$Acquire.open:')
    positive=bytecode.positive_path(factory,index+1,None,'nonnull')
    helper=bytecode.one([m for m in methods if bytecode.named(m,'closeLoginInput')],'one response adapter')
    empty=bytecode.index_of(helper,'InputStream.nullInputStream:')
    invoke=bytecode.index_of(helper,'ResourceScope.acquire:')
    ports=[o for o in helper['ops'][:invoke] if o[1]=='invokedynamic'][-3:]
    if len(ports)!=3 or helper['ops'][empty][0]>=ports[0][0]:
        raise ValueError('local no-resource absence representation and all ports before acquisition')
    caddy,_=bytecode.decode(run/'source','batch',package+'MorningCaddyReadiness$NativeIo')
    getter=bytecode.one([m for m in caddy if any('getErrorStream:' in o[2] for o in m['ops'])],'one conditional login getter')
    raw={}
    for needle in ('getErrorStream:','getInputStream:'):
        position=bytecode.index_of(getter,needle)
        raw[needle]=bytecode.positive_path(getter,position+1,None,'nonnull')
    verbose=subprocess.check_output([str(bytecode.JAVAP),'-p','-v','-classpath',
        str(run/'source/src/schubert-nk-batch/target/classes'),package+'MorningServiceReadiness$NativeIo'],text=True)
    refs=[line.strip() for line in verbose.splitlines() if 'REF_invokeVirtual java/net/' in line and '.getInputStream:()Ljava/io/InputStream;' in line]
    if not refs or any(not any(owner in line for owner in ('java/net/HttpURLConnection.getInputStream:',
            'java/net/URLConnection.getInputStream:')) for line in refs):
        raise ValueError('direct unchanged Java HTTP input factory reference')
    report=ET.parse(run/'source/src/schubert-nk-batch/target/site/jacoco/jacoco.xml').getroot()
    outer=bytecode.one([c for c in report.findall('package/class') if c.get('name')==package.replace('.','/')+'MorningCaddyReadiness'],'current controller counters')
    focused=[m for m in outer.findall('method') if m.get('name')=='closeLoginInput' or m.get('name').startswith('lambda$closeLoginInput$')]
    if len(focused)!=3:raise ValueError('helper and both implementation callbacks must be measured')
    focused_counters={m.get('name'):{c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))}
        for c in m.findall('counter') if c.get('type') in ('LINE','METHOD','BRANCH')} for m in focused}
    if any(c['missed'] for row in focused_counters.values() for c in row.values()):
        raise ValueError('all helper/callback line/method/branch counters must be100')
    value.update(nullableCaddyFactory={'method':factory['header'],'positiveNoHeapPcs':positive,**hashed},
        caddyRawGetterPositivePaths=raw,serviceDirectHttpFactoryReferences=refs,
        focusedCaddyHelperCounters=focused_counters,newJavaCases=6,realNullBodyAcquisitionsCounted=False,
        vmActions=0,testReplays=0,nativeOwnerExecutionQualified=False)
    proof.publish(entry,value,OUT)


if __name__=='__main__':main()
