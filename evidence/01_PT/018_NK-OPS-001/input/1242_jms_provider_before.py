"""Record source review and BUG/YKT before any provider-boundary implementation change."""
from pathlib import Path
import datetime as dt, hashlib, json, re, subprocess
R=Path.cwd(); B=R/'evidence/01_PT/018_NK-OPS-001'; E=B/'evidence'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
now=dt.datetime.now(dt.timezone.utc).isoformat(); head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
web='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/'
api='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/guard/'
names=['ArtemisReplyConsumer','ArtemisReplyConsumers','ArtemisReplyDlqSender','ArtemisRequestSender','CommittedFatalReplyException','JmsContextFactory','JmsReplyDecoder','JmsRequestReplyClient','JmsRequestReplyException','JmsRequestSender','MediaDescriptorWireClient','PendingReply','ProtectedReadWireClient','ProtectedReadWireException','ReplyCorrelationRegistry','ValidatedReply','WebBrokerContexts','package-info']
paths=[web+n+'.java' for n in names]+['src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/security/MqLoginClient.java']
assert len(paths)==19 and all((R/p).is_file() for p in paths)
affected=[web+'JmsReplyDecoder.java',api+'JmsMessageGuard.java']
tests=[p.replace('/main/','/test/').replace('.java','Test.java') for p in affected]
out=E/'PG26470-jms-provider-classification-before-v1';assert not out.exists();out.mkdir()
snap={}
for i,p in enumerate(affected+tests):
 target=out/(str(i+1)+'_'+Path(p).name+'.before.txt');target.write_bytes((R/p).read_bytes());snap[p]=dict(sha256=sha(R/p),snapshot=str(target.relative_to(R)))
ledger=R/'documents/900_OTHER/910_台帳'
bug=ledger/'915_障害表.md';ykt=ledger/'916_横展開管理台帳.md'
assert max(map(int,re.findall(r'BUG-(\d{3,})',bug.read_text())))==2658
assert max(map(int,re.findall(r'YKT-(\d{3,})',ykt.read_text())))==2338
bugtext='''
## BUG-2659（PG/PT、2026-11-12、JMS provider例外の恒久電文不正への誤分類、修正前）

対象JmsReplyDecoder.decode／JmsMessageGuard.read、PT-JMS-PROVIDER-WEB-001／PT-JMS-PROVIDER-API-001。重要度=高、優先度=高。期待=provider getterが返却せず投げた未知例外は元型・同一instanceで伝播し、不正な返却値だけをPermanentProtocolExceptionにする。実際=metadata構築全体のcatch IllegalArgumentExceptionがprovider内部IAEも捕捉し、恒久電文不正へ変換する。再現条件=独立BytesMessage ProxyでgetJMSMessageID等が固定IAEを投げる。既存7+7は不正返却値の試験で、provider投例外は未網羅。実行再現前、sourceで確認。誤ったDLQ/ACK/fatal判定へ波及し得るが、実brokerやDBへの発生は未確認。原因=provider取得と純値検査のcatch境界を共有。影響=Web/API二guardと呼出側分類、YKT-2339。

関連RD MQ-003/004/005/008/040..045、UI231/232、SS321§7/8・SS322§5・SSC332、411§5・451。承認済み仕様内の実装是正でRD/UI/SS変更不要、QA不要。修正予定=元のgetter/検査順を維持しprovider取得を変換catch外へ、UUID/Layout純変換のみ局所で固定診断へ。旧不正値・wire・null期待は変更せず独立provider故障二Testを追加。修正前source/head a72fec3031181fdb9c7f7d15e8874125ce3153ff／Main8b、before018/PG26470。再現・修正・再試験・coverage・commitは後記。状態OPEN、完了日未定。実経路/F03/全451は未受入。

'''
ykttext='''
## YKT-2339（PG/PT、2026-11-12、JMS取得と値検査の例外境界、修正前）

元BUG-2659。共通原因=provider getterを含むtry全体のIAEをwire恒久不正に変換。検索範囲Web messagingとAPI messaging/guardのcatch IllegalArgumentExceptionおよびgetter。対象一覧=JmsReplyDecoder／JmsMessageGuard二class。対象外=ArtemisReplyDlqSender.isCanonicalUuidは純文字列UUID検査のみ、ProtectedReadWireClient.requestPayloadは純固定長encodeのみでprovider取得なし。API/Web両側でgetter種別・property名ごとにIAE/NPE/Error/JMSExceptionの同一instance伝播、早期取得および不正返却値の元7+7を独立再試験する。検索のみで完了にせず、二class修正・再発防止Test・同source静的/coverage・未実行実経路の限界を記録する。修正commit・再試験証跡は後記、状態OPEN。

'''
for p,txt in [(bug,bugtext),(ykt,ykttext)]:
 s=p.read_text();a,b=s.split('\n',1);p.write_text(a+'\n'+txt+b)
held={'ArtemisReplyConsumers':'actual WebStartupException; service ownership','ArtemisRequestSender':'actual WebStartupException/provider transaction','WebBrokerContexts':'actual WebStartupException/credential/factory'}
review=[dict(path=p,sha256=sha(R/p),mainSourceRead='WHOLE',runtime='HOLD' if Path(p).stem in held else 'SOURCE_REVIEW_ONLY_NOT_RUNTIME_ADMISSION',reason=held.get(Path(p).stem,'individual whole Test/helper admission still required')) for p in paths]
v=dict(actualExit=0,observedAtUTC=now,source=head,productionCoreMain='8b2c6b8d4e76ecfb82eed729d6e3d548b87c0004',ownedMain19=review,wholeSafeCandidateTests=tests,defect='BUG-2659',horizontal='YKT-2339',beforeSnapshots=snap,originalP00502EstimateRetained=dict(low=.25,base=.65,high=1.3),additionalNormalBeforeEstimatePp=dict(low=.5,base=1.5,high=3),capPp=4,original190NewAcceptance=0,formalUpdated=False,productTestsExecuted=0,actualBrokerOrHeldOperations=False,partialRows=['WBS-P005-02/1','WBS-P005-02/2'],next='Beforeprice additional normal group; add independent provider fault matrices, run only new2 against original pinned guard source, then narrow Main2 fix/fresh static/necessary changed-source connected PT. Preserve all previous source/results, no runtime held4 or actual infrastructure.')
write(out/'manifest.json',v)
print(json.dumps(dict(actualExit=0,beforeManifest=str((out/'manifest.json').relative_to(R)),sha256=sha(out/'manifest.json'),defect='BUG-2659',sourceReview19=True,productTestsExecuted=0)))
