from datetime import datetime,timezone
from hashlib import sha256
import json,os,re,runpy,subprocess,tempfile,xml.etree.ElementTree as ET
from pathlib import Path
root=Path.cwd()
base=Path('evidence/01_PT/006_NK-MSG-002/evidence')
tool=Path('evidence/01_PT/006_NK-MSG-002/input/004_weblog_key_constructor_ownership.py')
h=runpy.run_path(str(tool)); W=h['WORK']
a,=base.glob('PG41352*/manifest.json')
b,=base.glob('PG41354*/manifest.json')
red=json.loads(a.read_bytes()); v=json.loads(b.read_bytes())
core=v['source']
assert len(red['constructorUnhitLines'])==3 and len(red['pmDrawSites'])==1
assert v['bytecodeProof']['productTests']==12
def pin(p):
    p=Path(p)
    return dict(path=str(p),sha256=sha256(p.read_bytes()).hexdigest())
assert all(pin(ref['path'])==ref for ref in (v['classfile'],v['bytecodeProof']['exec'],v['bytecodeProof']['xml'],v['protocolPackage']))
proof=v['bytecodeProof']
assert proof['finalValidation'] < proof['ownedKeyAllocations'][0] < min(proof['boundedArrayCopyCalls'])
runs=base/'PG41356-p01810-web-log-single-ownership-independent-v1'
work=W/runs.name
work.mkdir(mode=0o700)
j=h['TC']/'jdk-25.0.4/bin'
repo=h['TC']/'m2/repository'
classes=W/v['run']/'target/classes'
original=Path(proof['exec']['path'])
path=Path(v['classfile']['path'])
sources=W/v['run']/'src/main/java'/h['REL']
class_name=str(path.relative_to(classes).with_suffix(''))
reader=Path('tools/quality/jacoco_readonly_exec_subset.py')
exec_data=runpy.run_path(str(reader))['decode'](original.read_bytes(),{class_name})
crc=runpy.run_path('evidence/01_PT/018_NK-OPS-001/input/5593_p01808_original_name_binding.py')['class_id']
assert crc(path.read_bytes())==int(exec_data['classes'][class_name]['crc64'],16)
assert len(exec_data['sessions'])==1 and exec_data['sessions'][0]['labelBytesHex']==v['run'].encode().hex()
prev=Path('evidence/01_PT/020_NK-CHR-001/evidence/PG41272-p020-comparison-definitions-independent-v1/manifest.json')
precedent=json.loads(prev.read_bytes())
records={}
def run(label,args,exits=(0,)):
    argv=list(map(str,args))
    p=subprocess.run(argv,cwd=root,capture_output=True,check=False,timeout=110)
    o=work/(label+'.out'); o.write_bytes(p.stdout)
    e=work/(label+'.err'); e.write_bytes(p.stderr)
    records[label]=dict(argv=argv,exit=p.returncode,stdout=pin(o),stderr=pin(e))
    assert p.returncode in exits,(label,p.stderr[-300:])
    return o
jars=[repo/'org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar']
jars += [repo/f'org/ow2/asm/{n}/9.10.1/{n}-9.10.1.jar' for n in ('asm','asm-commons','asm-tree')]
cp=os.pathsep.join(map(str,jars))
analyzer=work/'analyzer'; analyzer.mkdir()
run('compile-strict-raw',[j/'javac','--release','25','-proc:none','-cp',cp,'-d',analyzer,root/'tools/quality/jacoco/UnfilteredCodeMeasurement.java'])
raw=run('original-coverage',[j/'java','-cp',str(analyzer)+os.pathsep+cp,'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement','--strict-original-exec','--line-deficits',original,path])
lines=raw.read_text().splitlines()
stats,=[s for s in lines if s.startswith('CLASS\t')]
ctor,=[s for s in lines if s.startswith('METHOD\t') and '\t<init>\t' in s and 'Ljava/security/SecureRandom;' in s]
draft=[s for s in lines if s.startswith('DEFICIT\t') and '\t<init>\t' in s]
assert not draft, draft
control=h['TC']/'static-gates-20261015/checkstyle-14.3.0-all.jar'
test=W/v['run']/'WebLogPayloadCodecTest.java'
style=run('checkstyle',[j/'java','-jar',control,'-c',root/'tools/quality/static/checkstyle.xml','-f','xml',sources/path.with_suffix('.java').name,test])
assert len(ET.parse(style).getroot().findall('file'))==2 and not ET.parse(style).getroot().findall('file/error')
fmt=h['TC']/'google-java-format-1.36.1-all-deps.jar'
run('format',[j/'java','-jar',fmt,'--dry-run','--set-exit-if-changed',sources/path.with_suffix('.java').name,test])
reference=precedent['steps']
ann=repo/'org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar'
arch=Path(v['protocolPackage']['path'])
typed=os.pathsep.join(map(str,(classes,ann,arch)))
spot=reference['spotbugs']['argv'][:reference['spotbugs']['argv'].index('-output')+1]
spot[spot.index('-auxclasspath')+1]=typed
sb=work/'spotbugs.xml'
run('spotbugs',[*spot,sb,path],(0,1))
sr=ET.parse(sb).getroot()
assert not sr.findall('.//BugInstance')+sr.findall('.//Error')+sr.findall('.//MissingClass')
pmd=reference['pmd']['argv'].copy()
pmd[pmd.index('--dir')+1]=str(sources/path.with_suffix('.java').name)
pmd[pmd.index('--aux-classpath')+1]=typed+os.pathsep+str(j.parent/'lib/jrt-fs.jar')
pm=work/'pmd.xml'; pmd[pmd.index('--report-file')+1]=str(pm)
run('pmd',pmd,(0,4))
pr=ET.parse(pm).getroot()
assert not pr.findall('.//{*}error')+pr.findall('.//{*}configerror')
sites=[]
src=(sources/path.with_suffix('.java').name).read_text().splitlines()
for el in pr.findall('.//{*}violation'):
    line=int(el.get('beginline'))
    sites.append(dict(line=line,method=el.get('method'),rule=el.get('rule'),lineSha256=sha256(src[line-1].strip().encode()).hexdigest()))
assert sites==[],sites
runs.mkdir()
out=runs/'constructor-coverage.tsv'
out.write_text(raw.read_text())
report=dict(run=runs.name,actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),core=core,commandResults=records,baseline=pin(a),qualified=pin(b),sameOriginalCoverage=pin(out),originalClass=pin(path),crc=hex(crc(path.read_bytes())),singleSession=1,scope='One exact WebLogPayloadCodec class; other four local Main inputs for symbol resolution only.',constructor=ctor,wholeLocalClass=stats,constructorUnhitLines=draft,pmDrawSites=sites,independentProbeSessionSourceRun=v['run'],checkstyleFindings=0,spotbugsFindings=0,rootNullAwayAndWerror=True,noJunitReexecution=True,actualAllocationErrorNotInjected=True,actualSecretOrBackendOperations=0,formalDelta=0,whole451=False)
(runs/'manifest.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(ctor)
print(stats)
print(sites)
