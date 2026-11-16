"""Dispose exactly169 J2EE-only PMD sites using pinned rule/architecture and per-site source/owner."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
import zipfile

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
prior=b/'evidence/PG36968-current287-pmd971-candidates-v2';manifest=load(prior/'manifest.json');assert manifest['actualExit']==0 and manifest['currentFindings']==971 and manifest['unmatched']==662
allrows=load(prior/'all-site-candidates.json');unmatched=load(prior/'unmatched-sites.json');assert len(allrows)==971 and len(unmatched)==662
assert len({x['rawFindingIndex'] for x in allrows})==971 and len({x['rawFindingIndex'] for x in unmatched})==662
assert sha(r/manifest['originalStatic']['path'])==manifest['originalStatic']['sha256']
jar=tc/'static-gates-20261015/pmd-bin-7.28.0/lib/pmd-java-7.28.0.jar'
with zipfile.ZipFile(jar) as z:
 xml=z.read('category/java/multithreading.xml');rules=ET.fromstring(xml);rule=next(x for x in rules.iter() if x.tag.rsplit('}',1)[-1]=='rule' and x.get('name')=='DoNotUseThreads');desc=next(x for x in rule if x.tag.rsplit('}',1)[-1]=='description');text=''.join(desc.itertext()).strip()
assert 'J2EE specification explicitly forbids' in text and 'J2EE server' in text
plan=next((r/'documents/400_PGPT/470_PMO').glob('485_*.json'));owners={x['path']:x for x in load(plan)['artifacts']}
doc='documents/300_SS/310_アプリケーション/311_モジュール・package・class責務設計.md';canonicalCommit=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip();canonical=subprocess.check_output(['git','show',canonicalCommit+':'+doc]);table=canonical.decode();assert 'Executable jar/oneshot' in table and '| `schubert-nk-batch`' in table
selected=[x for x in unmatched if x['raw']['rule']=='DoNotUseThreads'];assert len(selected)==169 and len({x['raw']['path'] for x in selected})==67
sites=[]
for item in selected:
 raw=item['raw'];path=r/raw['path'];data=path.read_bytes();assert hashlib.sha256(data).hexdigest()==item['sourceSha256'];assert raw['path'] in owners
 source=data.decode();lines=source.splitlines();line=lines[int(raw['beginline'])-1];assert line==item['actualSourceLine']
 assert raw['path'].startswith(('src/schubert-nk-bootstrap/src/main/java/','src/schubert-nk-batch/src/main/java/'))
 assert not any(x in source for x in ['import jakarta.ejb.','import javax.ejb.','import jakarta.enterprise.concurrent.','import javax.enterprise.concurrent.'])
 if any(x in line for x in ['isInterrupted','Thread.interrupted','Thread.currentThread().interrupt']):operation='CANCELLATION_INTERRUPT_STATE'
 elif any(x in line for x in ['threadId()','== owner','!= owner','private final Thread owner']):operation='SAME_THREAD_IDENTITY'
 elif any(x in line for x in ['UncaughtExceptionHandler','void fatal(Thread']):operation='STANDALONE_FATAL_BOUNDARY'
 elif any(x in line for x in ['Thread.sleep','onSpinWait','yield()']):operation='STANDALONE_POLL_PRIMITIVE'
 else:operation='STANDALONE_THREAD_OR_EXECUTOR_PRIMITIVE'
 owner=owners[raw['path']];sites.append(dict(rawFindingIndex=item['rawFindingIndex'],path=raw['path'],sourceSha256=item['sourceSha256'],line=int(raw['beginline']),column=int(raw['begincolumn']),className=raw.get('class'),method=raw.get('method'),rule=raw['rule'],actualSourceLine=line,owner=owner['owner'],costOwner=owner['costOwner'],operation=operation,decision='NOT_APPLICABLE_J2EE_CONTAINER_POLICY',reason='Pinned PMD7.28 rule forbids application-managed threading under J2EE managed server/EJB migration. This canonical standalone bootstrap/batch Java25 jar/oneshot executes under explicitly owned OS process, not a J2EE server/EJB. Interrupt/identity/worker primitive is governed by original SS311/341/342/343/354 and functional owner tests, not container-managed threading.',doesNotProveRuntimeConcurrencyOrNative=True))
assert {x['rawFindingIndex'] for x in sites}=={x['rawFindingIndex'] for x in selected}
remaining=[x for x in unmatched if x['rawFindingIndex'] not in {y['rawFindingIndex'] for y in sites}];assert len(remaining)==493
out=b/'evidence/PG37038-f03-j2ee169-applicability-v1';assert not out.exists();out.mkdir()
(out/'site-decisions.json').write_text(json.dumps(sites,ensure_ascii=False,indent=2)+'\n');(out/'remaining-unmatched.json').write_text(json.dumps(remaining,ensure_ascii=False,indent=2)+'\n')
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=manifest['sourceCore'],reviewOnly=True,productTestsExecuted=0,newAnalysisOrRegressionReplayed=False,totalOriginalRaw=971,oldCandidateUnconfirmed=309,newSourceMatchedFinalDispositions=169,remainingUnmatched=493,candidatePlusDispositionPlusUnknownIs971=309+169+493==971,allSources=67,sites=ref(out/'site-decisions.json'),remaining=ref(out/'remaining-unmatched.json'),prior=ref(prior/'manifest.json'),priorAllSites=ref(prior/'all-site-candidates.json'),ruleSource=dict(jarPath=str(jar),jarSha256=sha(jar),resource='category/java/multithreading.xml',resourceSha256=hashlib.sha256(xml).hexdigest(),rule='DoNotUseThreads',description=text),canonicalArchitecture=dict(path=doc,originMain=canonicalCommit,contentSha256=hashlib.sha256(canonical).hexdigest()),owners=ref(plan),noSourceRuleSuppressionChanges=True,wholeF03Accepted=False,newAcceptance=0,formalUpdated=False,effortCompletionRate=None)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
l=r/'documents/900_OTHER/910_台帳'
with (l/'915_障害表.md').open('a') as f:f.write('\n2026-11-17 BUG3147 限定CLOSED。既END5604をそのまま採用し、input4568で実registry正例及び分類/xml/工具path負3を検証、F03 START5605のみ一回発行。既価格ENDの再発行0、製品再実行0。証跡601/058とPG37034失敗保全、修正input4568のGit履歴。完了2026-11-17。\n')
with (l/'916_横展開管理台帳.md').open('a') as f:f.write('\n2026-11-17 YKT2616 限定CLOSED。当context全fieldと公開oracle md/jsonを実registryで純検証し正例/負3成功。START前検証完了後にSTART一回だけ発行、END5604が一件のまま確認。既4554/4565の正contextは再演せず、誤schema4567原本/失敗保全。修正4568/601-058/PG37034、完了2026-11-17。\n')
print(json.dumps(dict(actualExit=0,raw971Retained=True,sitesFinalClassified=169,files=67,remainingUnmatched=493,oldCandidatesUnconfirmed=309,newAcceptance=0)))
