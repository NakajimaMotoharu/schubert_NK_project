# P01625 共通四JSとCSS 四費用leaf契約対応

NK-WEB-002。対象source/hash、承認設計commit/hash、独立期待値/TestIDは [PG28030](../018_NK-OPS-001/evidence/PG28031-four-js-css-original-proof-join-v1/manifest.json)。

- P01625-PG01 / operation-post-submit.js wholeIIFE/event handler / PT-WEB-OPSJS2646-A..F,UI222§8: Eachform[data-operation-submit] ownsclosedtoken/buttonstructure andsubmittedboolean; missingtoken/nobutton failsfixedstructure, absentforms inert, invalidsubmit prevent/report withoutdisable, correctedvalid disablesallbuttons withoutchanginghiddenUUID, secondsubmit preventDefault, independentforms independentstate. No tokenissue/authgrant/businesssend/automatedretry; APIidempotency remainsserver authority.

- P01625-PG02 / question-input-validation.js wholeIIFE/validate/input/submit / PT-QST-JS001-A..H,QST-001: Absentform inert/closedquestion-remaining-button required, initialandinput NFC UTF8counter4096 minusbytecount withoutchangingrawvalue. 1..4096 required, malformedUTF16 viaencode-decode mismatch/allC0-C1-controls/trailingASCIIspace rejected; no trim, NBSP/fullwidthspace retained, BOMnotdiscarded, fixedvalidationmessage. Submitrevalidateswithoutinputevent/invalidprevent-report/validdisablesbutton, no automaticresend/UUIDrewrite. PublicDOMeventdouble isnot realbrowser/HTTP proof.

- P01625-PG03 / log-search-validation.js/search-speaker-submit.js wholeIIFE/validate/submit / PT-SCR092-A..H,PT-SCR025-A..H: Absentpage inert/closedcontrols; logq256-action64-path256 andScenarioq256-speaker128-chapter256 NFCUTF8 limits. FourrawCRLF-TAB-NUL andmalformedUTF16 rejected, JavaASCIItrim forbytevalidationonly/no rawrewrite, NBSP-BOM retained; immutablepercontrol events, allinvalidfieldschecked beforeprevent/report, correctedinput submit. Scenario gamechange requestSubmit nativevalidation anddoesnotbypassinvalidfield; no network orsession sourceaccess. Fullservervalidation remainsauthoritative.

- P01625-PG04 / schubert.css allselectors/media900/Currentretainedstyles / PT-SCR010,PT-SCR017..033,PT-SCR046..053,PT-SCR084..091,BUG2350/YKT2095: RetainedCurrentlogin/menu/scenario/search/animation/log scopedstyles, outlinefocus/pre-wrapbody/overflowtext; responsive900singlecolumns/sourceorder kept. Video1280shell/aspect16:9/viewport150; Music playerdownloadrules scopedmusic/song, missingplayerplaceholder andresponsive2→1. CSS sourcefullreview andoldtypedresources only, no inventCSSbranchcoverage/screenshot orrealbrowserCurrentcomparison.

- P01625-PG05 / Four existingNode harnesses andhistoricalresource proof / WBS-P016-25:contract,WBS-P016-25:scope,WBS-P016-25:quality: FourwholeexistingNodeTests 6+8+8+8=30 independentgoldenDOMevents/TextEncoder-Decoder/JDK-compatibleliteral vectors fullyread; publicold5Javawrappers/30Node case andresourceL-F-B100 areoldscopeonly. ExactcurrentJS/Test/Nodebinary andpublicmanifest/XMLsourcebindings checkedwithoutreexecute. No oldJavaJars/classinit orwholeMainqualification/currentformaltransfer; newPT/coverage/190accepted0. /1only, /2 realbrowser-CSS/CHR/sameMain451 remainunaccepted.

P01625原四費用leaf.01inventory/.02独立DOMfixture/.03JScoverage/.04CSS-HTMLsecrettraceの全五source418行と元Node全四TestをUI222223224225SS313352へ対応。正規625原八rowの開始総1/2.4/4.8を保持し四/1準備だけ.348/.84/1.68消化、架空parent/1を作らず/2と原190未受入。旧PG14778/80/82/84の公開manifest-chain/XML5wrapper/Node30-全4resourceLFB100・JS/Test/Node24.19本体hash一致を照合、製品試験再演0/新coverage0/JavaCP実体のread-hash0。旧wrapperコピーHTMLのquestions/new一差はmenuhref修正199d→a716（/menuからUI承認/）を検出し現JavaWrapper成功へ転用0。JS30は旧resource限定証拠のみ、CSS900実browser/CHR/全451-G07/trace閉鎖は未受入。

実行: `python3 -B evidence/01_PT/018_NK-OPS-001/input/1941b_original_subdivided_artifact_contract_stage.py audit evidence/01_PT/018_NK-OPS-001/input/1965b_four_js_css_subdivided_config.json ; python3 -B evidence/01_PT/018_NK-OPS-001/input/1967b_four_js_node_only_proof_metadata.py` metadata終了0。新規製品PT/coverageなし。原/1の準備だけ、原/2・451・元190未受入。独立期待値は公開設計の固定境界・順序・後条件に基づき、production methodで生成しない。正式1964PT/53scope・工数null。


## 2026-11-22 四scriptと変更HTMLの現候補

PG41666/41676で、四script・四独立fixture・Node V24.19.0の実体一致を確認。旧30子とL/F/Bを資源入力に紐付ける。質問入力HTMLのメニューhref差はNode fixtureから独立し、元Javaの外部script接続試験一件は差分対象。PG41668で明示7templateに対して単体一件合格。現実Browser・CSS表示差、451は未受入。
