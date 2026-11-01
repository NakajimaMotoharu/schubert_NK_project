"""Current successful proof/source binding only; no Product replay."""
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from source_evidence_binding import bind
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG17555-api-default-source-binding-v1'
RECORDS=[('PG17540-api-default-bind-one-pt-v1','378c67d9ed8d182d7aecbbcd65cc1f75c7369e73df6e166b108958aea431148a'),('PG17542-api-default-bind-one-post-v1','7f18c495eaa28389e1b233b6fafc9298ff954bb792f9fc46605a8d61f01d51ea'),('PG17544-api-default-bind-one-independent-v1','59e9990d6ebe91d5aa94eb31f1f87eb8cdc192b00692f2ae7bed23d9ad2ec6aa'),('PG17550-current2747-api-default-bind-registry-post-v1','8ae15e925d8af44a910f6dbd7dffe7368e2931089fbdf0bfec347f7cf15cb863'),('PG17554-current2747-api-default-bind-wbs-post-v1','c260507e91d2d501cc3fc99d4cefc787382d30577cdc90ff2b41a0744f34e74a')]
def main():
    invocation=capture(__file__);assert not OUT.exists()
    actual=bind([(data.BASE/n/'manifest.json',h) for n,h in RECORDS],SOURCE)
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,bindings=actual,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
