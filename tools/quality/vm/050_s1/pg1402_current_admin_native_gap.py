"""Same-source six host plus eight Root plus two actual ADMIN XML counter coordinates."""
import inspect
import pg1271_current_native_gap as previous
from pg1334_published_owned_stop_sources_v2 import SOURCE

NATIVE_SHA='c05911e9ddbf292c2375d155166fc8602bcc41345de47a15e8b7f723efdd1502'
HOST_SHA='1c21767249100f4716fc9bebb8de86081dca92cf86e5ad9ac158ba457d259e7b'

def source():
    raw=inspect.getsource(previous.main)
    raw=raw.replace('pg1258-fresh-ten-native-v1','pg1401-current-bootstrap-ten-native-v1').replace('pg1018-stream-six-host-v2','pg1279-held-channel-six-host-v1').replace('pg1271-current-native-gap-v1','pg1402-current-admin-native-gap-v1')
    raw=raw.replace("record['qualifiedCurrentNativeSubcampaign']is True and ",'')
    marker="    modules=('protocol','storage','bootstrap','api','web','batch');data=[]"
    raw=raw.replace(marker,"    prior_base=W/'pg1341-published-eight-native-v1';require(sha(prior_base/'manifest.safe.json')=='99ace9ae4497d33c331700ec656502e543de2e64192ba5350b4f1dfa456f4d71'and record['previousEightManifestSha256']==sha(prior_base/'manifest.safe.json'));prior=json.loads((prior_base/'manifest.safe.json').read_bytes())\n"+marker)
    raw=raw.replace("record['hostExecHashes']","prior['hostExecHashes']")
    raw=raw.replace("require(len(record['selected'])==10)","require(len(prior['selected'])==8)")
    raw=raw.replace("enumerate(record['selected'])","enumerate(prior['selected'])").replace("p=cohort/(str(i)+'.exec')","p=prior_base/(str(i)+'.exec')")
    marker='    require(len(data)==16)'
    raw=raw.replace(marker,"    post=json.loads((W/'pg1400-existing-admin-independent-post-v1.safe.json').read_bytes());require(record['bootstrapPostManifestSha256']==sha(W/'pg1400-existing-admin-independent-post-v1.safe.json'))\n    for i,v in enumerate(post['bootstrap']['files']):\n        p=cohort/('bootstrap-'+str(i)+'.exec');require(p.stat().st_size==v['bytes']and sha(p)==v['sha256']==record['bootstrapNativeHashes'][i]);data.append(p)\n"+marker)
    compile(raw,'<current ADMIN ten native coordinate extraction>','exec');return raw

def main():
    env=dict(previous.__dict__,SOURCE=SOURCE,NATIVE_SHA=NATIVE_SHA,HOST_SHA=HOST_SHA)
    exec(compile(source(),'<new same-source current ADMIN gap>','exec'),env);return env['main']()

if __name__=='__main__':raise SystemExit(main())
