"""Only a local JMS-aware finite graph classifier and the one outer catalog guard."""
from pathlib import Path
import ast,hashlib,json,subprocess,xml.etree.ElementTree as ET
import pg9666_pagination_static as c
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';O=B/'evidence/PG27816-read-wire-catalog-source-static-v1';source='edaf641333266660ec79a6e070c98b7a79bbccac';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=json.loads((B/'evidence/PG27814-read-wire-catalog-before-v1/before.json').read_text());assert not O.exists()
base=R/'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging';wire=base/'ProtectedReadWireClient.java';exception=base/'JmsRequestReplyException.java';old={p:subprocess.check_output(['git','show',source+':'+str(p.relative_to(R))],text=True) for p in [wire,exception]};assert all(sha(p)==before['inputHashes'][str(p.relative_to(R))] for p in old)
helper=B/'input/1634_web_security_fatal_source_static.py';tree=ast.parse(helper.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['revert_calls','require_owned']],type_ignores=[]),str(helper),'exec'),globals())
pattern='        | DateTimeException failure) {\n';call='      JmsRequestReplyException.preserveFatal(failure);\n';assert old[wire].count(pattern)==1;new=old[wire].replace(pattern,pattern+call);assert revert_calls(new,[call])==old[wire]
reference=R/'src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/StorageIoException.java';s=reference.read_text();signature='  public static void preserveFatal(Throwable failure) {';method=s[s.index(signature):s.rindex('\n}')]
end='''      if (candidate instanceof java.sql.SQLException sql) {
        java.sql.SQLException next = sql.getNextException();
        if (next != null) pending.add(next);
      }
''';linked='''      // JMSException keeps linkedException separately from Throwable.cause.
      if (candidate instanceof jakarta.jms.JMSException jms) {
        Exception linked = jms.getLinkedException();
        if (linked != null) pending.add(linked);
      }
''';assert method.count(end)==1;method=method.replace(end,end+linked);comment='\n  /** BUG2721/YKT2359: preserve fatal identity before a secret-free JMS catalog conversion. */\n'
planned={wire:new,exception:old[exception].removesuffix('}\n')+comment+method+'\n}\n'};assert planned[exception].replace(comment+method+'\n','')==old[exception]
for p,v in planned.items():assert require_owned(p.read_text(),old[p],v) is False
for p,v in planned.items():p.write_text(v)
O.mkdir();c.SLOT=O;jdk=TC/'jdk-25.0.4/bin';sg=TC/'static-gates-20261015';paths=list(map(str,planned))
stages=dict(format=c.step('format',[str(jdk/'java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',*paths],R),checkstyle=c.step('checkstyle',[str(jdk/'java'),'-jar',str(sg/'checkstyle-14.3.0-all.jar'),'-c',str(R/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(O/'checkstyle.xml'),*paths],R))
passed=all(v['actualExit']==0 and not v['timedOut'] for v in stages.values()) and not ET.parse(O/'checkstyle.xml').findall('.//error')
m=dict(actualExit=0 if passed else 1,sourceBefore=source,inputHashes={str(p.relative_to(R)):sha(p) for p in old},stages=stages,originalSourceInverseExact=True,localHelperExactAlgorithmReuse=dict(path=str(reference.relative_to(R)),sha256=sha(reference),onlyAdditionalCarrier='jakarta.jms.JMSException.getLinkedException',identityVisited=True),catalogCallsOnly=1,normalReasonsResourceOwnershipAndCleanupUnchanged=True,productTestsExecuted=0,MainCompiled=False,MainInitializedOrInvoked=False,coverage=None,ptStatus='NOT_RUN_NOT_PASS',bug='BUG-2721',actualHeldClassBinaryAccess=False,actualBrokerDbRootVmOperations=0,verifierSha256=sha(Path(__file__).resolve()))
(O/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');assert passed;print(json.dumps(dict(actualExit=0,changedSources=2,catalogCalls=1,manifestSha256=sha(O/'manifest.json'))))
