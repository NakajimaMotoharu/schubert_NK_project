"""Five config-only fmt/adapt cases, no validate/provision/daemon/TLS/key/target action."""
import ast
import copy
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
from host_tool_invocation import capture,verify
from public_blob_scan import sha
from caddy_public_format_contract import equal

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
SLOT=ROOT.parent/'pgpt-runs/PG379/pg9012-caddy-format-static-v1'
OUT=BASE/'PG9012-caddy-format-static-v1'
SOURCE='f690fa6be336550f8078e2bdde40ef34ab5efe6b'
BINARY=ROOT.parent/'characterization-tools/root/usr/bin/caddy'
BINARY_SHA='678c1849799e6d81c7cfbe63cebb8f92400cb70a67fc9f601697cb8ce7cdfa4a'
ARTIFACT='src/deployment/caddy/Caddyfile.template'
REFERENCE=ROOT/'tools/quality/pg6948_c01_static_adapt.py'
REFERENCE_SHA='5e2b928aa3dd6d8c60e8439433d29da27151041096aee1a5e435bc59f4f70753'
DESIGN='documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md'


def write(path,value):
    with path.open('x',encoding='utf-8') as stream:
        json.dump(value,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')


def verifier():
    assert sha(REFERENCE.read_bytes())==REFERENCE_SHA
    nodes=[node for node in ast.parse(REFERENCE.read_text()).body if isinstance(node,ast.FunctionDef) and node.name in {'walk','verify_json'}]
    assert len(nodes)==2
    namespace={'__builtins__':{'isinstance':isinstance,'dict':dict,'list':list,'len':len,'any':any,'ValueError':ValueError}}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(REFERENCE),'exec'),namespace)
    return namespace['verify_json']


def step(name,mode,input_path):
    command=([str(BINARY),'fmt',str(input_path)] if mode=='fmt' else
             [str(BINARY),'adapt','--config',str(input_path),'--adapter','caddyfile'])
    assert mode in {'fmt','adapt'}
    env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','HOME':str(SLOT),
         'XDG_CONFIG_HOME':str(SLOT/'xdg-config'),'XDG_DATA_HOME':str(SLOT/'xdg-data')}
    start=dt.datetime.now(dt.timezone.utc).isoformat()
    write(SLOT/(name+'-begin.safe.json'),dict(command=command,startUTC=start,source=SOURCE,
          inputSha256=sha(input_path.read_bytes()),binarySha256=BINARY_SHA))
    child=subprocess.Popen(command,cwd=SLOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    ticks=(Path('/proc')/str(child.pid)/'stat').read_text().rsplit(')',1)[1].split()[19]
    write(SLOT/(name+'-process.safe.json'),dict(pid=child.pid,startTicks=ticks,command=command,cwd=str(SLOT),source=SOURCE))
    try:stdout,stderr=child.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        child.kill();child.communicate();raise TimeoutError('own static Caddy deadline') from None
    terminal=dict(actualExit=child.returncode,endUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
         stdoutBytes=len(stdout),stdoutSha256=sha(stdout),stderrBytes=len(stderr),stderrSha256=sha(stderr))
    write(SLOT/(name+'-terminal.safe.json'),terminal)
    assert child.returncode==0 and 0<len(stdout)<1024*1024
    warnings=[];unknown=0
    for line in stderr.decode('utf-8').splitlines():
        matches=[header for header in ('X-Forwarded-For','X-Forwarded-Proto','X-Forwarded-Host') if 'Unnecessary header_up '+header in line]
        if len(matches)==1:warnings.append('SS_REQUIRED_EXPLICIT_'+matches[0])
        else:unknown+=1
    assert unknown==0 and (not stderr if mode=='fmt' else len(warnings)==3 and len(set(warnings))==3)
    assert not (SLOT/'xdg-config').exists() and not (SLOT/'xdg-data').exists()
    with (OUT/(name+'.output.txt')).open('xb') as stream:stream.write(stdout)
    return stdout,dict(caseId=name,command=command,startUTC=start,terminal=terminal,
                        inputSha256=sha(input_path.read_bytes()),classifiedWarnings=warnings,unclassifiedWarnings=unknown)


def main():
    invocation=capture(Path(__file__));assert not SLOT.exists() and not OUT.exists()
    assert sha(BINARY.read_bytes())==BINARY_SHA
    template=(ROOT/ARTIFACT).read_bytes()
    assert template==subprocess.check_output(['git','show',SOURCE+':'+ARTIFACT],cwd=ROOT)
    assert sha(template)=='2914bfd4134186911562071f92652ce750e513213a749672dd161615c3d8763c'
    design=subprocess.check_output(['git','show','origin/main:'+DESIGN],cwd=ROOT).decode()
    blocks=re.findall(r'```caddyfile\n(.*?)\n```',design,re.S);assert len(blocks)==1
    no_comments='\n'.join(line for line in template.decode().splitlines() if not line.lstrip().startswith('#'))
    equal(blocks[0],no_comments)
    check_json=verifier()
    rejected=[]
    for name,before,after in [('quoted-value','"nosniff"','"no sniff"'),('body','2MB','2MiB'),
        ('port',':55160',':55161'),('upstream','127.0.0.1:8080','127.0.0.2:8080'),
        ('timeout','60s','61s'),('header','X-Frame-Options','X-Other-Header')]:
        changed=template.decode().replace(before,after,1);assert changed!=template.decode()
        try:equal(template.decode(),changed)
        except ValueError:rejected.append(name)
        else:raise AssertionError('logical Caddy change accepted as format')
    for name,text in [('unclosed-quote','header "broken'),('empty','')]:
        try:equal(template.decode(),text)
        except ValueError:rejected.append(name)
        else:raise AssertionError('invalid format accepted')
    SLOT.mkdir(mode=0o700);OUT.mkdir()
    rendered={'template':template}
    for name,address in [('ipv4','127.0.0.1'),('ipv6','2001:db8::1')]:
        site=address if ':' not in address else '['+address+']'
        rendered[name]=template.decode().replace('https://<GLOBAL_IP>','https://'+site).replace('<GLOBAL_IP>',address).encode()
    inputs={}
    for name,data in rendered.items():
        path=SLOT/(name+'.Caddyfile')
        with path.open('xb') as stream:stream.write(data)
        inputs[name]=path
    cases=[]
    for number,name in enumerate(('template','ipv4','ipv6'),1):
        stdout,row=step('PT-C01-FMT-'+str(number).zfill(3),'fmt',inputs[name])
        assert stdout==rendered[name]
        row['fixedPoint']=True;cases.append(row)
    semantic_guards=[]
    for number,name,address in [(4,'ipv4','127.0.0.1'),(5,'ipv6','2001:db8::1')]:
        stdout,row=step('PT-C01-FMT-'+str(number).zfill(3),'adapt',inputs[name])
        value=json.loads(stdout);check_json(value,address)
        # Counterexamples are not expected values: independent oracle remains SS fixed constants.
        for mutation in ('admin','listener','trust'):
            changed=copy.deepcopy(value)
            if mutation=='admin':changed['admin']['disabled']=False
            elif mutation=='listener':next(iter(changed['apps']['http']['servers'].values()))['listen']=['0.0.0.0:55160']
            else:changed['apps']['pki']['certificate_authorities']['local']['install_trust']=True
            try:check_json(changed,address)
            except ValueError:semantic_guards.append(name+'-'+mutation)
            else:raise AssertionError('unsafe static profile accepted')
        row['independentSsSemanticsConfirmed']=True;cases.append(row)
    assert (ROOT/ARTIFACT).read_bytes()==template
    verify(invocation)
    value=dict(actualExit=0,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
        source=SOURCE,artifact=ARTIFACT,artifactSha256=sha(template),binarySha256=BINARY_SHA,
        designRef='origin/main',designSha256=sha(design.encode()),referenceVerifierSha256=REFERENCE_SHA,
        staticCases=cases,staticCaseCount=5,formatCounterexamples=rejected,semanticCounterexamples=semantic_guards,
        formatWarnings=0,unclassifiedWarnings=0,requiredExplicitHeaderWarningsPerAdapt=3,
        actualDaemonOrVmOrTlsOrProvisionActions=0,privateCredentialReads=0,targetServiceConnections=0,
        xdgStateCreated=False,legacyMainOrImportsExecuted=False,javaProductTestsExecuted=0,
        productCoverage=None,wholeC01Or451Accepted=False,formalUpdated=False,newAccepted=0)
    write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,staticCases=5,formatWarnings=0,formatCounterexamples=len(rejected),semanticCounterexamples=len(semantic_guards),daemonOrVmActions=0)))


if __name__=='__main__':main()
