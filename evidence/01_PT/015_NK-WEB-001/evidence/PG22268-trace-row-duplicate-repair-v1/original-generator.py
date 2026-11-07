from pathlib import Path
import json,hashlib,datetime
r=Path.cwd();load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=r/'evidence/01_PT/015_NK-WEB-001/evidence/PG22228-exception-factory-independent-post-v1/manifest.json';m=load(p);assert (m['actualExit'],m['tests'],m['sourceProofNew'])==(0,4,1)
ref=dict(path=str(p.relative_to(r)),sha256=sha(p));now=datetime.datetime.now().astimezone().isoformat();result=r/'evidence/01_PT/015_NK-WEB-001/081_例外Filter生成・一回SavedGET単体結果.md'
result.write_text('''# NK-WEB-001 例外Filter生成・一回SavedGET単体結果

- 仕様: 080_例外Filter生成・一回SavedGET単体仕様.md。PT-WEB-EXCEPTION-FACTORY全4method、Test source aa101fb7c3c8b53d5218ca6dd3bd8db2973eb493、Main 7aed8eace7c844c2f79f2e39db766faf914890d5、独立Verifier 54f21243574b296c02b6e0e8234ccca45f006dbd。
- 事前compile PG22216 javac25 lint/Werror0。静的PG22218はrawPMD1/exit4を既fixtureのDataSource defining-loader一件として個別非該当、適用0/Checkstyle0/六Main解析0。Java25.0.4、固定JUnit1.13.4/Spring-test7.0.9、OS/JDK/command/input/依存hashは下記manifest。
- PG22220元Unitは4成功、failed/error/skipped/aborted0、真正終了0。収集wrapperは存在しない匿名$1 classを期待して終了1。BUG2422/YKT2167を修正前起票し元collector/失敗証跡22222を保持した。Product/Testを再実行せず、22224受動metadata回収0、22228独立照合0で原XML・exec・入力byte不変/同sourceを確認した。実行と収集の終了コードを混同しない。
- target全Code: instruction20/line5/method2/class1はmissed0。branchは自然零・N/Aで比率100としない。原一exec/session/CRCと正常Jar内の唯一のclassを照合。旧exec合算/手動除外なし。17support classの実methodとsource限定lambda4を確認し、support全source資格へ転用しない。
- 独立literal oracle: fresh Filter/null拒否/同一entrypoint、GET navigationは302/Location=/login・relative savedGET文字列一回だけ、POST/AJAX/mediaと空context拒否は403/監査理由、通常/IOExceptionは同一object転送・session/監査0。Mock Servlet・同owner heap fixture・空ThreadLocal内で確認。実principal/認証付与/DBsession/暗号/wire/Root/nativeを実行せず、それらの受入に転用しない。
- 実行command: `python3 -B evidence/01_PT/015_NK-WEB-001/input/027_exception_factory_independent_post.py`（受動独立postのみ）。元Unit command/終了/環境は原unit-exit.safe.jsonとXMLに保存。実際4/新unique4/新source1、正式1964PT/53scope・新leaf0・工数率nullを維持する。

Manifest: `'''+ref['path']+'` SHA256 `'+ref['sha256']+'`。全公開file hashはmanifest.files、原生存・機密・業務dataの追加採取なし。\n')
p=next((r/'documents/400_PGPT').rglob('441_実装判断記録.md'));assert 'PG-D1145' not in p.read_text();p.write_text(p.read_text()+'''\n\n## PG-D1145：例外Filter生成と一回SavedGETはSDKの実委譲を同owner単体で検証する（2026-11-07）

Main WebAccessExceptionFilterFactoryを変更せず、NullRequestCacheによりSDK既定SavedRequestの保存を抑え、業務handlerの相対GET文字列だけが一回保存されることをwhole新4methodで直接確認する。SDK Filterの実chainを通し、固定302/403/location・String write回数・監査event/reason・object identityを独立期待値とする。空ThreadLocalのAccessDeniedはSDKの委譲分岐であって実ユーザROLEの資格ではない。Mock heap session/audit callbackは実行した事実として明記し、実sessionDBやcryptoを実行0と分ける。

収集は対象normal Jarの実family一classをUnit前に照合する。Unit後のcollector故障は元XML/exec/sourceを保持し、実行を繰り返さず受動metadataだけ回収する（BUG2422/YKT2167）。target全Code L5M2C1達成、branch自然0/N-A、support17と既成功をsource資格へ転用しない。015080/081・22216/18/20/22/24/28。canonical owner/cost WBS-P015-02一群、承認仕様/設計/DIF/全HOLD/正式/451不変。\n''')
p=next((r/'documents/400_PGPT').rglob('431_Module・Program一覧.md'));p.write_text(p.read_text()+'''\n\n### 2026-11-07 例外Filter生成・SavedGET単体

| Program/class/method | 関連設計・判断 | Test・証拠 | canonical owner/cost |
|---|---|---|---|
| NK-WEB-001 WebAccessExceptionFilterFactory constructor/create | 015080のRD/UI/SS対応・PG-D1145 | 015080/081、新whole4/PG22220・独立22228、L5M2C1未達0/branch自然0N-A | WBS-P015-02、群一回 |
| 支援 WebAccessFailureHandler/EncryptedSessionRequestCache/Mock owner fixture | 同上、302/403/一回String保存・監査literal | 同runのsupport17実method限定、whole source信用0。実認証/DB/session暗号/HTTP/Root/nativeは別未受入 | 既所有不変/追加費配賦0 |
''')
p=r/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json';raw=p.read_text();inv=json.loads(raw);key='currentExceptionFilterFactoryQualification20261107';assert key not in inv
rows=[]
for path,h in m['inputHashes'].items():
 if path.endswith('.java'):rows.append(dict(path=path,sha256=h,source=m['source'],productionCoreMain=m['productionCoreMain'],role='TARGET_OR_EXPLICIT_TEST_SUPPORT',newAcceptance=False))
target='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/security/WebAccessExceptionFilterFactory.java';rows.append(dict(path=target,sha256=sha(r/target),source=m['source'],productionCoreMain=m['productionCoreMain'],role='TARGET',newAcceptance=False))
overlay=dict(source=m['source'],productionCoreMain=m['productionCoreMain'],manifest=ref,record=str(result.relative_to(r)),rows=rows,newTestPath='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/security/WebAccessExceptionFactoryPortTest.java',newUniqueTests=4,requalifiedExistingTests=0,newSourceProofs=1,sourceProofRetained=0,branchStatus=m['branchStatus'],parentAccepted=False,wholeG13Accepted=False)
assert raw.rstrip().endswith('}');new=raw.rstrip()[:-1]+',\n  '+json.dumps(key)+': '+json.dumps(overlay,ensure_ascii=False,indent=2)+'\n}\n';parsed=json.loads(new);del parsed[key];assert parsed==inv;p.write_text(new)
p2=r/'documents/400_PGPT/470_PMO/486_WBS現行実績.json';raw2=p2.read_text();v=json.loads(raw2);old=v['inventorySha256'];raw2=raw2.replace('"inventorySha256": "'+old+'"','"inventorySha256": "'+sha(p)+'"',1);v2=json.loads(raw2);v2['inventorySha256']=old;assert v2==v;p2.write_text(raw2)
for fn,ident in [('915_障害表.md','BUG-2422'),('916_横展開管理台帳.md','YKT-2167')]:
 p=r/'documents/900_OTHER/910_台帳'/fn;p.write_text(p.read_text()+'\n\n### '+ident+' 有限collector修正CLOSED（'+now+'）\n\n原因は別factoryの匿名$1期待の転記。024修正はexact一classとUnit前family照合、原collector/失敗22222保持。横展開は当factory collector/Unit前検査/metadata回収/独立post全対象へ反映し、既別factoryの実匿名class前提は変更しない。再発防止は実Jarfamily集合の完全一致とpostのsame-byte/全Code/CRC検査。修正commit54f212435、22224回収0/22228独立0、元Unit4/OS0は再実行0。Test/Main/oracle期待値は変更なし。証跡015081・PG22222/24/28、完了日2026-11-07、他runtime品質の閉鎖ではない。\n')
print(json.dumps(dict(actualExit=0,manifest=ref,inventorySha256=sha(r/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json'))))
