# WBS現行source測定bindingの正規更新（内部必要依存、2026-10-15）

## 事実・境界

477/487/460、WBS-G13.07内の必要計測stage。485/486のsourceとmeasurementBindingは969d8/PG540、check_acceptanceはそのsourceと同じ受入証拠を要求する。これは正しいfail-closed条件であり緩めない。一方、現941artifactのgit diff a9..HEADは全件差0で、現在のsource実証はa9/PG2802、同Mainで新3701試験集合を統合する3274/3276/3278が進行中。旧sourceを新成果へ偽装するのでも、941を未検証のまま受入へ算入するのでもなく、同一byte/sourceの実測定基点を更新してから個別受入を判定する。

Main/外部仕様/RD/UI/SS/DIF/QA051/正式1964-53/品質/モデルは変更しない。941artifact/815outer/共有37/190task/252leaf/281RD/64layout/費用原-v3は固定。QA/RDF/UIC/SSC不要、上位仕様より詳細な管理・計測の内部判断。G13.07終了依存を早期準備の禁止とは解釈せず、このstageだけでG13を認定しない。

## 必要証拠と手順

1. 3276の実3701/542/1643/FES0/static六0と、3278の同a9実28異session/全1643Main79resource-debug同byte/CRCを要求。未実行・別source・旧件数・失敗・欠落は拒否する。元host/native原manifestと六union XMLの原hashを固定し、既Root/VM/業務処理を再発行しない。
2. 専有aruの当new-only原manifestと六XMLだけをpinned mini SSHで私有領域へ読取転送。秘密/鍵/DB/原本/全logの転送は禁止。原hashと実counterを検証してから公開projectionを作る。XMLのtechnical sessioninfo IDはSHA化し、原XMLhashとprojection hashを分ける。Counter/class/method/line内容の変更0を構造比較し、raw session/cookie/tokenをGitへ置かない。
3. 現941artifactのhashとa9..HEAD全差0、未commit変更なしを再検査。485の旧source/binding/hashは履歴へ保存し、現source=a9・新測定bindingへ更新する。486も同source/run/inventoryhashとし、全190rowを同六データで再分類。旧selected override/分類/sourceは履歴保存し、新defaultデータが完全に対象moduleを含む場合だけ置換する。counter不足・未知・非Javaは未達のまま。
4. check_acceptanceの同source・全criteria・証拠hash・終了依存条件は不変更。更新前後のwbs_progress_audit、source/hash/件数/失敗/欠落の負例を要求する。ここではacceptance一件も変更せず、工数null/正式1964-53を維持する。
5. その後、別の個別要求/独立oracle/TestID/全対象/品質/終了依存matrixを監査し、満たしたleafだけ認定する。技術再分類数を当期の新PG成果や工数率としない。

## 実装・保全

PG3280工具は準備/適用を分離し、原input/manifest/hash・旧485/486 byteを私有保全、公開証拠とsource binding更新を意味ある単位でcommit/pushする。新生成証拠を固定してからsource更新を適用し、既存dirty/他の更新があればhash不一致で拒否する。Bulk JSON更新では対象root field/190rowだけを機械更新し、他current observation/旧比較/費用を保持する。公開pathはrepo相対をROOT基準で解決して再現可能にし、旧private絶対path bindingも履歴検証に維持する。

状態=設計・着手見積り保存済み、実source binding更新/受入は未実施。stage見積.25/.75/2ppは既G13.07 .72/2/4.5の内数で追加leaf/予算加算ではない。共有枠/実token/PGPTとPMOの配賦は不明値nullのまま、元/v3予測を消さない。
