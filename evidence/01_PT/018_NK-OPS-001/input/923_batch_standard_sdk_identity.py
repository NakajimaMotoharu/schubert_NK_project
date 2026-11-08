"""Metadata-only identity of SDK classes observed in original73 own-JVM run; no SDK PT/coverage qualification."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess,zipfile
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';E=B/'evidence';RUNS=R.parent/'pgpt-runs/PG379';TC=R.parent/'toolchain';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_bytes());raw=E/'PG25260-batch-standard-original-whole73-v1/manifest.json';assert sha(raw)=='26e09b1962cf7b8201d9e90027325ee96df233e722e01e6a0686b78255ed9265';m=load(raw);assert m['actualExit']==0;ref=m['begin']['preflight'];assert sha(R/ref['path'])==ref['sha256'];pf=load(R/ref['path']);run=RUNS/'pg25260-batch-standard-original-whole73-v1';positive={}
for line in (run/'execinfo.stdout').read_text().splitlines():
 hit=re.fullmatch(r'\s*([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(.+)',line)
 if hit and hit[4].startswith(('io/micrometer/','io/prometheus/','org/HdrHistogram/')) and int(hit[2])>0:assert hit[4] not in positive;positive[hit[4]]=hit[1]
assert len(positive)==132 and all(n.startswith(('io/micrometer/','io/prometheus/','org/HdrHistogram/')) for n in positive)
S=RUNS/'pg25264-batch-standard-sdk-identity-v1';O=E/'PG25264-batch-standard-sdk-identity-v1';assert not S.exists() and not O.exists();S.mkdir();O.mkdir();(S/'classes').mkdir();priorPath=E/'PG25234-batch-text-sdk-identity-v1/manifest.json';assert sha(priorPath)=='a1b915ebbef7289a45ae928441e9f6170a744b1d84828e6b0f22ec1f0c6a7bee';prior=load(priorPath);old={n:r['crc64'] for n,r in prior['classRows'].items() if n in positive};assert len(old)==128 and all(old[n]==positive[n] and prior['classRows'][n]['jarSha256']==pf['vendorJars'][prior['classRows'][n]['jarPath']] for n in old);rows={}
for path,digest in pf['vendorJars'].items():
 assert sha(Path(path))==digest
 with zipfile.ZipFile(path) as jar:
  for n in sorted(positive):
   member=n+'.class'
   if member not in jar.namelist():continue
   assert n not in rows and not any(v.startswith('META-INF/versions/') and v.endswith('/'+member) for v in jar.namelist());b=jar.read(member);rows[n]=dict(jarPath=path,jarSha256=digest,classSha256=hashlib.sha256(b).hexdigest(),crc64=positive[n])
   if n not in old:
    target=S/'classes'/member;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
assert set(rows)==set(positive);p=subprocess.run([str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'org.jacoco.cli-0.8.15-nodeps.jar'),'classinfo',str(S/'classes')],capture_output=True,text=True,timeout=60);(S/'classinfo.stdout').write_text(p.stdout);(S/'classinfo.stderr').write_text(p.stderr);assert type(p.returncode) is int and p.returncode==0;crcs={}
for line in p.stdout.splitlines():
 hit=re.fullmatch(r'\s*\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+class 0x([0-9a-f]{16}) (\S+)',line)
 if hit:assert hit[2] not in crcs;crcs[hit[2]]=hit[1]
assert set(crcs)==set(positive)-set(old) and all(positive[n]==v for n,v in crcs.items());initializers=set(re.findall(r"Initializing '([^']+)'",(run/'class-init.log').read_text()));sdkinit={n.split('$$Lambda+',1)[0] for n in initializers if n.startswith(('io/micrometer/','io/prometheus/','org/HdrHistogram/'))};assert all(n in rows or any((n+'.class') in zipfile.ZipFile(path).namelist() for path in pf['vendorJars']) for n in sdkinit);assert all(n.startswith(('io/micrometer/','io/prometheus/','org/HdrHistogram/')) for n in sdkinit);assert not any(n.startswith(('io/opentelemetry/','io/prometheus/metrics/exporter/','io/prometheus/metrics/tracer/otel')) for n in sdkinit);otelPropertyTypes=sorted(n for n in sdkinit if 'OpenTelemetry' in n);assert otelPropertyTypes==['io/prometheus/metrics/config/ExporterOpenTelemetryProperties','io/prometheus/metrics/config/ExporterOpenTelemetryProperties$Builder']
(O/'classinfo-new4.txt').write_bytes((S/'classinfo.stdout').read_bytes());v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),producerManifestSha256=sha(raw),sdkPositiveClasses=len(positive),newSdkMetadataClasses=len(crcs),reusedSdkMetadataClasses=len(old),classRows=rows,normalizedSdkInitializerNames=sorted(sdkinit),productTestsExecuted=0,allObservedSdkCrcMatch=True,sdkIdentityOnlyNotCoverage=True,sdkRuntimeInitializedByThisMetadata=False,actualOwnJvmPublicMetricsRead=True,otelExporterOrTracerInitialized=False,otelConfigPropertyTypesOnly=otelPropertyTypes,actualExternalCollectorOrExportActions=0,files={p.name:sha(p) for p in O.iterdir()});(O/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(actualExit=0,sdkClasses=len(rows),newMetadata=len(crcs),reused=len(old),manifestSha256=sha(O/'manifest.json'))))
