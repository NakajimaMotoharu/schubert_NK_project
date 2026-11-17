"""Review borrowed directory/JDBC/stdio aliases without creating or closing any target resource."""
from pathlib import Path
import collections
import datetime
import hashlib
import json

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
prior=b/'evidence/PG37078-f03-owner-visibility7-applicability-v1';previous=load(prior/'manifest.json');left=load(prior/'remaining-unmatched.json');selected=[x for x in left if x['raw']['rule']=='CloseResource'];assert len(selected)==29
owners={x['path']:x for x in load(next((r/'documents/400_PGPT/470_PMO').glob('485_*.json')))['artifacts']};sites=[];counts=collections.Counter()
for x in selected:
 raw=x['raw'];path=r/raw['path'];text=path.read_text();lines=text.splitlines();n=int(raw['beginline']);assert sha(path)==x['sourceSha256'] and lines[n-1]==x['actualSourceLine']
 if path.name=='InspectorLockHandoff.java':
  category='JDBC_ALIAS';assert 'try (var statement = parent.prepareStatement(sql))' in text and 'try (var row = checkedStatement.executeQuery())' in text
  reason='present(statement)/present(row) are nonnull aliases of the identical enclosing two TWR-owned JDBC children; no acquisition occurs at the warning. Parent Connection is borrowed. Duplicating close on alias would violate once-only ownership.'
 elif path.name in ['CaddyPublicConfiguration.java','MaintenanceRunFiles.java','RootFailedStartRecovery.java']:
  category='BORROWED_DIRECTORY_ALIAS';assert '.get(' in x['actualSourceLine'] or '.getLast()' in x['actualSourceLine'] or 'for (var marker : markers)' in x['actualSourceLine']
  reason='This reference comes from an already-held caller/scoped directory-or-marker list (held/views/roots/markers). The local view does not acquire or transfer ownership. Existing outer ResourceScope/nested owners retain and close the object; closing a borrowed view here would invalidate sibling/readback/retirement ownership. This ownership-only disposition neither executes recovery nor resolves BUG3152 or any HOLD.'
 elif path.name=='BackupArchiveProcess.java':
  category='STDIO_ALIAS';assert 'Objects.requireNonNull(stream' in x['actualSourceLine']
  reason='owned is a typed nonnull alias of the private already-owned stdio stream. writeAndClose closes its owner on success, while the enclosing process/resource owner handles write/close uncertainty and retains failures. The local alias creates no second resource or close obligation.'
 elif path.name in ['BackupUnitStartClient.java','MaintenanceUnitStopClient.java']:
  category='STDIO_ALIAS';assert 'getInputStream()' in x['actualSourceLine'] or 'Closeable stderr;' in x['actualSourceLine']
  assert 'closeOne(stdout);' in text and 'return closeOne(stderr) && clean;' in text and 'if (!closed) return Status.UNKNOWN;' in text
  reason='Captured stdout/stderr belong to the same existing client Attempt, not a new client or detached resource. If stderr lookup fails, stdout close is attempted; normal closeBoth attempts both and failure remains UNKNOWN/poisoned. Automatic TWR alias close or false known termination would change the explicit resource contract; actual start/stop/native proof remains held/separate.'
 else:
  category='JDBC_ALIAS';assert 'finally' in text and ('JdbcResourceFailures' in text or 'JdbcAdmissionFailures' in text)
  reason='present/required aliases the same already-acquired Statement/ResultSet. Original references are closed once by nested explicit finally and the source-defined SS332/343 priority helper, including body/row/close failures; the Connection remains borrowed. Intraprocedural PMD alias tracking does not see that owner. Actual JDBC fault matrix/DB/authority is not proved by this policy disposition.'
 counts[category]+=1;owner=owners[raw['path']];sites.append(dict(rawFindingIndex=x['rawFindingIndex'],path=raw['path'],sourceSha256=x['sourceSha256'],line=n,column=int(raw['begincolumn']),rule=raw['rule'],method=raw.get('method'),actualSourceLine=x['actualSourceLine'],sourceContext=lines[max(0,n-3):n+4],owner=owner['owner'],costOwner=owner['costOwner'],category=category,decision='NOT_APPLICABLE_BORROWED_OR_ALREADY_OWNED_ALIAS',reason=reason,functionalOrActualResourceTestsReplaced=False))
assert counts==dict(JDBC_ALIAS=19,BORROWED_DIRECTORY_ALIAS=5,STDIO_ALIAS=5)
indices={x['rawFindingIndex'] for x in sites};assert len(indices)==29;remaining=[x for x in left if x['rawFindingIndex'] not in indices];assert len(remaining)==156
out=b/'evidence/PG37080-f03-owned-alias29-applicability-v1';assert not out.exists();out.mkdir();(out/'site-decisions.json').write_text(json.dumps(sites,ensure_ascii=False,indent=2)+'\n');(out/'remaining-unmatched.json').write_text(json.dumps(remaining,ensure_ascii=False,indent=2)+'\n')
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=previous['sourceCore'],reviewOnly=True,newFinalDispositions=29,aliasCategories=dict(counts),finalWithPrior=815,remainingUnmatched=156,unconfirmedReuseCandidates=0,totalOriginalRaw=971,all971Reconciled=815+156==971,prior=ref(prior/'manifest.json'),sites=ref(out/'site-decisions.json'),remaining=ref(out/'remaining-unmatched.json'),sourceRuleSuppressionChanges=0,productTestsExecuted=0,actualRootNativeStartStopRecoveryOperations=0,bug3152StillOpen=True,newAcceptance=0,wholeF03Accepted=False,formalUpdated=False,effortCompletionRate=None)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,aliases=29,categories=dict(counts),final=815,remaining=156,newAcceptance=0)))
