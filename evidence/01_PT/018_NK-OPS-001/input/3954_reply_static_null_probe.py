"""Four expected NullAway errors, calibrated by valid Main compile0; never executes these callers."""
from pathlib import Path
import hashlib,json,re,shutil,xml.etree.ElementTree as ET
import pg9666_pagination_static as c
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pp=b/'evidence/PG34942-reply-values-prepare-v1/manifest.json';p=ld(pp);assert p['actualExit']==0 and p['stages']['nullaway-compile']['actualExit']==0 and not p['stages']['nullaway-compile']['timedOut'];positive=r.parent/'pgpt-runs/PG379/pg34942-reply-values-v1';w=r.parent/'pgpt-runs/PG379/pg34948-reply-null-static-v1';o=b/'evidence/PG34948-reply-static-null-four-v1';assert not w.exists() and not o.exists();w.mkdir();o.mkdir();c.SLOT=o;shutil.copyfile(positive/'pom.xml',w/'pom.xml');shutil.copytree(positive/'src',w/'src');assert sha(w/'pom.xml')==p['subsetPomSha256'];ns='{http://maven.apache.org/POM/4.0.0}';ET.register_namespace('',ns[1:-1]);compiler=next(x for x in ET.parse(w/'pom.xml').getroot().findall('.//'+ns+'plugin') if x.findtext(ns+'artifactId')=='maven-compiler-plugin');assert hashlib.sha256(ET.tostring(compiler)).hexdigest()==p['rootCompilerSha256'];text='''package dev.codex.schubert.nk.quality;
import dev.codex.schubert.nk.web.messaging.ValidatedReply;
import dev.codex.schubert.nk.web.messaging.CommittedFatalReplyException;
import dev.codex.schubert.nk.web.messaging.JmsContextFactory;
import java.util.UUID;
final class ReplyNullBoundaryProbe {
  static void invalidInputs() {
    new ValidatedReply(null, new byte[0]); // NULL_ID
    new ValidatedReply(new UUID(0, 1), null); // NULL_BODY
    new CommittedFatalReplyException(null); // NULL_CAUSE
  }
  static JmsContextFactory invalidFactory() {
    return () -> null; // NULL_RETURN
  }
}
''';f=w/'src/main/java/dev/codex/schubert/nk/quality/ReplyNullBoundaryProbe.java';f.parent.mkdir(parents=True,exist_ok=True);f.open('x').write(text);(o/'negative-caller.java.txt').open('x').write(text);cases=[dict(testId=f'PT-REPLY-NULLSTATIC{i+1:03}',sourceLine=n,marker=line.split('// ',1)[1],expected='NULLAWAY_ERROR_NOT_RUNTIME_EXECUTION') for i,(n,line) in enumerate((n,line) for n,line in enumerate(text.splitlines(),1) if '// NULL_' in line)];assert len(cases)==4;before={n:sha(r/n) for n in p['inputHashes']};step=c.step('negative-null-compile',[str(tc/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'),'-o','--no-transfer-progress','-Dstyle.color=never','-Dmaven.repo.local='+str(tc/'m2/repository'),'-Dmaven.test.skip=true','compile'],w,timeout=180);log=(o/'negative-null-compile.stdout').read_text()+(o/'negative-null-compile.stderr').read_text();lines={int(x) for x in re.findall(r'ReplyNullBoundaryProbe\.java(?::\[|\[|:)(\d+)(?:,\d+)?(?:\]|:)[^\n]*\[NullAway\]',log)};v=dict(actualExit=0 if step['actualExit']==1 and not step['timedOut'] and lines=={x['sourceLine'] for x in cases} else 1,expectedCompilerExit=1,actualCompilerExit=step['actualExit'],positiveMainCompile=ref(pp),sameRootCompilerConfiguration=True,rootCompilerSha256=p['rootCompilerSha256'],badFixtureSha256=sha(f),badFixture='negative-caller.java.txt',expectedCases=cases,observedDiagnosticSourceLines=sorted(lines),stages={'negative-null-compile':step},applicationTestsExecuted=0,productionClassOrFixtureRuntimeInvocation=0,normalJUnitTestsNotIncremented=True,coverageNotIncremented=True,inputHashes=before,source='01cc280064936775e0377371edb3cdf1fa4f1139',newAcceptance=0);assert before=={n:sha(r/n) for n in before};(o/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=v['actualExit'],expectedCompilerExit=1,actualCompilerExit=step['actualExit'],observedLines=sorted(lines),expectedLines=[x['sourceLine'] for x in cases],runtimeTestsExecuted=0)));raise SystemExit(v['actualExit'])
