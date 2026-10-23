"""Only one hash-qualified internal test library/property; ordinary quality semantics unchanged."""
import xml.etree.ElementTree as ET

PROPERTY='schubert.pt.protocol.jar'
COORDINATES={'groupId':'dev.codex.schubert','artifactId':'schubert-nk-protocol',
  'version':'0.1.0-SNAPSHOT','scope':'system','systemPath':'${'+PROPERTY+'}'}

def verify_harness(before,after,qualified_path):
    old=ET.fromstring(before);new=ET.fromstring(after)
    old_deps=old.find('{*}dependencies');deps=new.find('{*}dependencies')
    if old_deps is None or deps is None:raise ValueError('exact original dependencies required')
    selected=lambda n:n.findtext('{*}groupId')==COORDINATES['groupId'] and n.findtext('{*}artifactId')==COORDINATES['artifactId']
    found=[n for n in deps if selected(n)]
    if any(selected(n) for n in old_deps) or len(found)!=1:raise ValueError('one new test-only protocol binding')
    node=found[0]
    if len(node)!=5 or {n.tag.rsplit('}',1)[-1]:n.text for n in node}!=COORDINATES:
        raise ValueError('exact normal production artifact/version and immutable system-path property')
    props=new.find('{*}properties')
    if old.find('{*}properties') is not None or props is None or len(props)!=1 or props[0].tag.rsplit('}',1)[-1]!=PROPERTY or props[0].text!=qualified_path:
        raise ValueError('only exact qualified artifact path, not stale M2 or arbitrary library')
    deps.remove(node);new.remove(props)
    for root in (old,new):
        for element in root.iter():
            element.text=element.text.strip() if element.text and element.text.strip() else None
            element.tail=None
    if ET.tostring(old)!=ET.tostring(new):raise ValueError('all parent/compiler/PT/four100/static/SDK semantics unchanged')
    return dict(added=COORDINATES,qualifiedPath=qualified_path,qualitySemanticsUnchanged=True,
      productionPomChanged=False,m2Overwritten=False,newExclusions=False,newDownload=False)
