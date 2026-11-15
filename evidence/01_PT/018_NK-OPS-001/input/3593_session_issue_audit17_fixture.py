"""Only two old pool lifetimes change; invert every edit before writing and preserve all business oracles."""
from pathlib import Path
import hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';closure=json.loads((b/'evidence/PG33970-session-issue-audit17-source-closure-v1/manifest.json').read_text());records=[];changes=[]
for path,count in [('src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/SessionIssueJdbcPortTest.java',8),('src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/SessionAuditPortTest.java',9)]:
 p=r/path;old=p.read_text();assert old.count('@Test')==count and hashlib.sha256(old.encode()).hexdigest()==closure['inputHashesBefore'][path]
 a='try (var workers = Executors.newFixedThreadPool(2)) {';z='var workers = Executors.newFixedThreadPool(2);\n    try {';assert old.count(a)==1;s=old.replace(a,z)
 if count==8:a2='''        assertEquals(i % 2 == 0 ? 3 : 5, results.get(i).get(5, TimeUnit.SECONDS));
    }
  }
}'''
 else:a2='''      assertBindings(second.get(5, TimeUnit.SECONDS), "EXPIRED", new SqlNull(Types.VARCHAR));
    }
  }'''
 z2=a2.replace('\n    }\n  }','\n    } finally {\n      workers.shutdownNow();\n      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));\n    }\n  }');assert s.count(a2)==1;s=s.replace(a2,z2)
 s=s.replace('import org.junit.jupiter.api.Test;','import org.junit.jupiter.api.Test;\nimport org.junit.jupiter.api.Timeout;').replace('final class '+p.stem+' {','@Timeout(value = 30, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)\nfinal class '+p.stem+' {')
 reverse=s.replace('import org.junit.jupiter.api.Timeout;\n','').replace('@Timeout(value = 30, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)\n','').replace(z2,a2).replace(z,a);assert reverse==old and s.count('@Test')==count and s.count('workers.shutdownNow();')==1 and s.count('assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));')==1
 records.append(dict(path=path,oldSha256=hashlib.sha256(old.encode()).hexdigest(),newBeforeFormatSha256=hashlib.sha256(s.encode()).hexdigest(),oldDefinitions=count,newDefinitions=0,changes=[dict(old=a,new=z),dict(old=a2,new=z2)],originalBusinessAssertionsInverseExact=True));changes.append((p,s))
e=b/'evidence/PG33971-session-issue-audit17-fixture-inverse-v1';assert not e.exists();e.mkdir()
for p,s in changes:p.write_text(s)
(e/'manifest.json').open('x').write(json.dumps(dict(actualExit=0,sourceBefore=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),records=records,expectedTests17=True,newDefinitions0=True,onlyPoolFinallyAndClassTimeout=True,applicationTestsExecuted=0,bug='BUG3031',horizontal='YKT2546'),ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,old17AssertionsInverseExact=True,pools2Finite=True)))
