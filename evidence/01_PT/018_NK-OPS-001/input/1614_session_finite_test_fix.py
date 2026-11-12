"""BUG2705 full fixture lifetime only, original assertion byte inverse preserved."""
from pathlib import Path
import hashlib,json,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG27388-session-finite-test-source-v1';assert not O.exists();rows=[]
for name in ['SessionAttributeCodecTest','SessionPayloadCodecTest','WebSessionIdTest']:
 p=R/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session'/(name+'.java');old=subprocess.check_output(['git','show','fa9b9fa81706b0e62a34c3bd374a3971c2495499:'+str(p.relative_to(R))],text=True);assert p.read_text()==old;s=old;pairs=[]
 for n in ([10,2] if name=='SessionPayloadCodecTest' else [10]):
  a=f'    try (var pool = Executors.newFixedThreadPool({n})) {{';z=f'    var pool = Executors.newFixedThreadPool({n});\n    try {{';assert s.count(a)==1;s=s.replace(a,z);pairs.append((a,z))
 if name=='SessionAttributeCodecTest':
  a='      for (var future : futures) future.get(20, TimeUnit.SECONDS);\n    }\n  }';z='      for (var future : futures) future.get(20, TimeUnit.SECONDS);\n    } finally {\n      pool.shutdownNow();\n      if (!pool.awaitTermination(10, TimeUnit.SECONDS)) {\n        throw new AssertionError("session attribute workers did not terminate");\n      }\n    }\n  }';assert s.count(a)==1;s=s.replace(a,z);pairs.append((a,z))
 elif name=='WebSessionIdTest':
  a='      for (var future : futures) future.get(20, TimeUnit.SECONDS);\n    }\n    assertEquals(100, ids.size());';z='      for (var future : futures) future.get(20, TimeUnit.SECONDS);\n    } finally {\n      pool.shutdownNow();\n      if (!pool.awaitTermination(10, TimeUnit.SECONDS)) {\n        throw new AssertionError("session identity workers did not terminate");\n      }\n    }\n    assertEquals(100, ids.size());';assert s.count(a)==1;s=s.replace(a,z);pairs.append((a,z))
 else:
  a='    } finally {\n      codec.close();\n    }\n  }';z='    } finally {\n      pool.shutdownNow();\n      if (!pool.awaitTermination(10, TimeUnit.SECONDS)) {\n        throw new AssertionError("session payload nonce workers did not terminate");\n      }\n      codec.close();\n    }\n  }';assert s.count(a)==1;s=s.replace(a,z);pairs.append((a,z))
  a='    } finally {\n      release.countDown();\n      codec.close();\n    }\n  }';z='    } finally {\n      release.countDown();\n      pool.shutdownNow();\n      if (!pool.awaitTermination(10, TimeUnit.SECONDS)) {\n        throw new AssertionError("session payload close workers did not terminate");\n      }\n      codec.close();\n    }\n  }';assert s.count(a)==1;s=s.replace(a,z);pairs.append((a,z))
 inverse=s
 for a,z in reversed(pairs):assert inverse.count(z)==1;inverse=inverse.replace(z,a)
 assert inverse==old;p.write_text(s);rows.append(dict(path=str(p.relative_to(R)),oldSha256=hashlib.sha256(old.encode()).hexdigest(),newSha256=hashlib.sha256(p.read_bytes()).hexdigest(),originalAllAssertionsInverseExact=True,changes=[dict(before=a,after=z) for a,z in pairs]))
O.mkdir();v=dict(actualExit=0,bug='BUG-2705',horizontal='YKT-2374',sourceBefore='fa9b9fa81706b0e62a34c3bd374a3971c2495499',TestChanged3=True,ownedPools4=True,allOriginalAssertionsInverseExact=True,rows=rows,productTestsExecuted=0,actualBackendOrHeldClassActions=0);(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,changedTestSources=3,pools=4)))
