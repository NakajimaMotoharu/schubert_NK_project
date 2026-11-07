"""Explicit storage Test source static tools, no Test compilation/run or Product initialization."""
from pathlib import Path
import datetime,hashlib,json,re,stat,subprocess,sys,xml.etree.ElementTree as E
import pg9666_pagination_static as c
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';F=B/'evidence/PG22796-storage-static-inputs-v1';OUT=B/'evidence/PG22798-storage-all-test-static-v1';SLOT=R.parent/'pgpt-runs/PG379/pg22798-storage-all-test-static-v1';TC=R.parent/'toolchain';JDK=TC/'jdk-25.0.4/bin'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def inputs():
 rows={}
 for raw in subprocess.check_output(['git','ls-files','--stage','-z','--','src/schubert-nk-storage/src/test/java'],cwd=R).split(b'\0'):
  if not raw:continue
  meta,n=raw.decode().split('\t',1);mode,oid,stage=meta.split();assert mode=='100644' and stage=='0' and n.endswith('.java') and not any(x in n for x in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_']);p=R/n;assert stat.S_ISREG(p.lstat().st_mode) and not p.is_symlink();data=p.read_bytes();assert subprocess.check_output(['git','hash-object','--stdin'],cwd=R,input=data).decode().strip()==oid;rows[n]=dict(gitBlob=oid,sha256=hashlib.sha256(data).hexdigest())
 assert len(rows)==29;return dict(sorted(rows.items()))
def main():
 config=B/'input/261_storage_test_static_scope.json';cfg=load(config);assert cfg['module']=='storage' and cfg['expectedSourceCount']==29 and cfg['sourcePrefix']=='src/schubert-nk-storage/src/test/java/' and not any(cfg[k] for k in ['productExecutionAllowed','originalTestCompileAllowed','nativeAccessEnabled']);normal=R.parent/'pgpt-runs/PG379/pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';nm=load(normal);assert nm['actualExit']==0 and nm['source']=='7aed8eace7c844c2f79f2e39db766faf914890d5';jar=Path(nm['jars']['storage']['path']);assert sha(jar)==nm['jars']['storage']['sha256'];head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();now=datetime.datetime.now().astimezone().isoformat()
 if sys.argv[1:] == ['freeze']:
  assert not F.exists();F.mkdir();write(F/'manifest.json',dict(actualExit=0,atJST=now,source=head,productionCoreMain=nm['source'],inputs=inputs(),scopeConfig=dict(path=str(config.relative_to(R)),sha256=sha(config)),normalManifestSha256=sha(normal),normalModuleJar=dict(path=str(jar),sha256=sha(jar)),productTestsExecuted=0));print('frozen29');return
 assert not sys.argv[1:];assert not OUT.exists() and not SLOT.exists();f=load(F/'manifest.json');assert sha(config)==f['scopeConfig']['sha256'];assert inputs()==f['inputs'];assert sha(jar)==f['normalModuleJar']['sha256']
 for p in [Path(__file__),config,F/'manifest.json']:assert p.read_bytes()==subprocess.check_output(['git','show',head+':'+str(p.relative_to(R))],cwd=R)
 console=TC/'junit-platform-console-standalone-1.13.4.jar';assert sha(console)=='3fdfc37e29744a9a67dd5365e81467e26fbde0b7aa204e6f8bbe79eeaa7ae892';js=TC/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar';aux=[jar,console,js];sg=TC/'static-gates-20261015';rules=R/'tools/quality/static';pmd=[sg/'record-fix-v1/pmd-record-1298.jar',*sorted((sg/'pmd-bin-7.28.0/lib').glob('*.jar'))];fmt=load(B/'evidence/PG21744-explicit-ordinary-test-format-audit-v1/manifest.json')['stage']['command'];fmt=fmt[:fmt.index('com.google.googlejavaformat.java.Main')+1];SLOT.mkdir();c.SLOT=SLOT;listing=SLOT/'sources.txt';listing.write_text(''.join(str(R/n)+'\n' for n in f['inputs']))
 commands=dict(pmd=[str(JDK/'java'),'-cp',':'.join(map(str,pmd)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--aux-classpath',':'.join(map(str,aux)),'--no-cache','--format','xml','--report-file',str(SLOT/'pmd.xml')],checkstyle=[str(JDK/'java'),'-jar',str(sg/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(SLOT/'checkstyle.xml'),'@'+str(listing)],format=fmt+['--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',*f['inputs']]);stages={}
 for label,cmd in commands.items():cmd[1:1]=['-Xlog:class+init=info:file='+str(SLOT/(label+'-class-init.stdout'))];stages[label]=c.step(label,cmd,R,timeout=180)
 reports={}
 for label,tag in [('pmd','violation'),('checkstyle','error')]:
  root=E.parse(SLOT/(label+'.xml')).getroot();items=[]
  for parent in root.iter():
   if parent.tag.rsplit('}',1)[-1]=='file':
    path=str(Path(parent.get('name')).relative_to(R));assert path in f['inputs']
    for x in parent:
     if x.tag.rsplit('}',1)[-1]==tag:items.append(dict(path=path,**x.attrib,message=' '.join(''.join(x.itertext()).split())[:600],classification='UNCLASSIFIED'))
  errors=[dict(x.attrib) for x in root.iter() if label=='pmd' and x.tag.rsplit('}',1)[-1] in ['error','configerror']];reports[label]=dict(rawItems=items,rawCount=len(items),processingErrors=errors)
 init={label:sorted(set(re.findall(r"Initializing '(dev/codex/schubert/nk/[^']+)",(SLOT/(label+'-class-init.stdout')).read_text()))) for label in stages};assert all(not v for v in init.values());assert inputs()==f['inputs'];assert not any(s['timedOut'] for s in stages.values());OUT.mkdir();files={}
 for p in SLOT.iterdir():
  if p.is_file():q=OUT/p.name;q.write_bytes(p.read_bytes());files[p.name]=sha(q)
 formatjars=[Path(part) for arg in fmt for part in arg.split(':') if part.startswith(str(TC)) and part.endswith('.jar')];assert formatjars;toolfiles=[*pmd,*aux,*formatjars,sg/'checkstyle-14.3.0-all.jar',rules/'pmd.xml',rules/'checkstyle.xml',TC/'jdk-25.0.4/release'];manifest=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=head,productionCoreMain=nm['source'],freeze=dict(path=str((F/'manifest.json').relative_to(R)),sha256=sha(F/'manifest.json')),inputHashes={n:v['sha256'] for n,v in f['inputs'].items()},dependencies={str(p):sha(p) for p in toolfiles},reports=reports,stages=stages,productInitializations=init,checkedSources=29,sourceBytesUnchanged=True,productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,applicableFindings=None,allFindingsClassified=False,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,files=files,producer=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)));write(OUT/'manifest.json',manifest);print(json.dumps(dict(actualExit=0,pmdRaw=reports['pmd']['rawCount'],checkstyleRaw=reports['checkstyle']['rawCount'],formatExit=stages['format']['actualExit'],productInitializations=0)))
if __name__=='__main__':main()
