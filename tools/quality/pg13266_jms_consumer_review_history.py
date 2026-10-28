"""Immutable accounting transition; later sources cannot rewrite the reviewed historical source."""
import g07_host_class_provenance_inputs as data
from pg13258_current_catalog_supplement import state_after as previous_state

def state_after():
    path = data.BASE/'PG13262-jms-consumer-purpose-review-v1'
    m = data.read_checked(path/'manifest.json','21035e3b63cb7a03ecbdc3c95496bd8c21d53d73de5cf365fd540ebec10bca46')
    v = data.read_checked(path/'review.json',m['reviewSha256'])
    post = data.read_checked(data.BASE/'PG13264-jms-consumer-purpose-post-v1/manifest.json','b0ba0d554deb628cfddd8363a36cb583ffff2a6496a71c25251d02163c8e9736')
    assert post['actualExit'] == post['productTestsExecuted'] == post['newAccepted'] == 0 and post['independentOriginalIds'] == 72
    assert post['reviewManifestSha256'] == data.sha((path/'manifest.json').read_bytes()) and post['metadataNegativeVectors'] == 8
    assert v['source'] == post['source'] == 'db33c6a371d3dbc8e84f70462e0e56351bbb18b4'
    ids,refs,pending = previous_state();new = {r['id'] for r in v['rows']}
    assert len(new) == 72 and len(v['rows']) == 72 and new <= ids-refs
    assert all(r['manualPurposeReviewComplete'] is True and r['actualViolation'] is None and r['ptExecutionExempt'] is False for r in v['rows'])
    result = ids,refs|new,pending|new
    assert [len(x) for x in result] == [8022,3345,1255]
    return result
