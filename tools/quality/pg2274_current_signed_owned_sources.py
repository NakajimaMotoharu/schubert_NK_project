"""BUG1224: new-only owned graph, exact current release and signature stem."""
from pyflakes.api import check
import pg2246_newboot_owned_sources as prior

SOURCE=prior.SOURCE
BOM=prior.BOM
TOOLS='pg2274-current-signed-owned-stop-tools-v1'
context=prior.context


def sources():
    result={}
    for name,raw in prior.sources().items():
        name=name.replace('2246','2274')
        raw=raw.replace(prior.TOOLS,TOOLS).replace('Pg2246','Pg2274').replace('pg2246','pg2274').replace('PG2246','PG2274')
        if name=='Pg2274NativeStop.java':
            marker='Pg387TrustedDeployment.STEM="pg1846"'
            if raw.count(marker)!=1:raise ValueError('one exact historical stem defect required')
            raw=raw.replace(marker,'Pg387TrustedDeployment.STEM="pg2126"')
        if name.endswith('.py'):
            if check(raw,'<actual signed-current owned graph>'):raise ValueError('whole current namespace required')
            compile(raw,'<actual signed-current owned graph>','exec')
        result[name]=raw
    return result

