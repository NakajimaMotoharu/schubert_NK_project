"""Bind completed same-source MVC15 and finite actual imports; no Product rerun."""
import ast
import importlib.util
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG17801-web-mvc-source-binding-v1'
RECORDS=[["PG17782-owned-mvc-loopback-runner-metadata-v1","1da064d3efbce8bf4993d28635aafa001fea5c1aa90724993cff8f79b1dccd0f"],["PG17784-owned-mvc-loopback-environment-binding-v1","cc09737223363737e2f09dbb47ee2f76733ca38949c80d1d9b21126f688ad60c"],["PG17785-web-mvc-loopback-review-v1","be30d8bdc377c6598ba10dee605954cffdb906874a8847999c1ec4c450d189e3"],["PG17786-web-mvc-loopback-fifteen-pt-v1","f7f82c9e3d5606ce8b54d484cb09e0ceca353b1cf00952248c40cc4da7dea58d"],["PG17788-web-mvc-loopback-fifteen-post-v1","404e3c94fb1fb6be7444c86647c38b53fa071a68d22fc0783a40120822c97bfb"],["PG17790-web-mvc-loopback-fifteen-independent-v1","d225d063d29c2ddc19761c0ddb7f8d36c1ed58d36ce694e8c5dd77ca79ee0561"],["PG17794-current2825-web-mvc-registry-v1","8aceaae95f920ed2be0304a68972a104f557a1ac24cfc89bfebf58f3bbc70dfe"],["PG17796-current2825-web-mvc-registry-post-v1","fbb0e6f616ca8608a085b8664929984f4b6ce69687e08c0d6b169f7a31e23089"],["PG17798-current2825-web-mvc-wbs-v1","15a86ac9690430075f6bfd54bb27ffa3e7e785bf7c6dd0bc742aba43ec68c854"],["PG17803-current2825-web-mvc-wbs-post-v2","44e398131aa7046400be1edcd31f49284e45087949e863215e325745b7064ff4"]]
FILES=["pg17782_owned_mvc_loopback_runner_metadata.py","pg17784_owned_mvc_loopback_environment_binding.py","pg17786_web_mvc_loopback_fifteen_pt.py","pg17788_web_mvc_loopback_fifteen_post.py","pg17790_web_mvc_loopback_fifteen_independent.py","pg17794_current2825_web_mvc_registry_v1.py","pg17796_current2825_web_mvc_registry_post_v1.py","pg17798_current2825_web_mvc_wbs_v1.py","pg17803_current2825_web_mvc_wbs_post_v2.py"]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    rows=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    actual_imports={}
    for name in FILES:
        path=data.ROOT/'tools/quality'/name;tree=ast.parse(path.read_text());imports=[]
        for node in ast.walk(tree):
            names=[v.name for v in node.names] if isinstance(node,ast.Import) else [node.module] if isinstance(node,ast.ImportFrom) and node.level==0 else []
            for value in names:
                if value and (value.startswith('pg') or value.startswith('scoped_prometheus') or value.startswith('owned_mvc')):
                    assert importlib.util.find_spec(value) is not None
                    imports.append(value)
        actual_imports[name]=dict(sha256=data.sha(path.read_bytes()),existingToolImports=sorted(set(imports)),qualifiedByOriginalSuccessfulInvocation=True)
    bad=data.ROOT/'tools/quality/pg17800_current2825_web_mvc_wbs_post_v1.py'
    assert data.sha(bad.read_bytes())=='c61118410059613fa21b8a35a5b344eb6f2b4402f8e342dce9a25aa9ccf81d52'
    assert importlib.util.find_spec('pg17798_current2825_receipt_owned_graph_wbs_v1') is None
    fixed=data.read_checked(data.BASE/RECORDS[-1][0]/'manifest.json',RECORDS[-1][1])
    assert fixed['writerBindingNegativeVectors']==2 and fixed['metadataNegativeVectors']==29 and fixed['ordinaryDeclarationNegativeVectors']==4
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=rows,finiteImportAndHashAudit=actual_imports,failedEntrySha256=data.sha(bad.read_bytes()),failedOriginalBodyExit=1,failedProductTestsExecuted=0,correctedMetadataOnly=True,correctedWriterBindingNegativeVectors=2,original15Reexecuted=False,writerReexecuted=False,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
