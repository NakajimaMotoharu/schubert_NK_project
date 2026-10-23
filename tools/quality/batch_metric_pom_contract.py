"""Exactly one installed same-SDK Batch compile dependency, all other semantic XML unchanged."""
import xml.etree.ElementTree as ET

def verify_batch_core_pom(before,after):
    old=ET.fromstring(before);new=ET.fromstring(after)
    old_deps=old.find('{*}dependencies');deps=new.find('{*}dependencies')
    if old_deps is None or deps is None:raise ValueError('both original dependency lists required')
    old_nodes=[n for n in old_deps if n.findtext('{*}groupId')=='io.micrometer'
      and n.findtext('{*}artifactId')=='micrometer-core']
    added=[n for n in deps if n.findtext('{*}groupId')=='io.micrometer'
      and n.findtext('{*}artifactId')=='micrometer-core']
    if old_nodes or len(added)!=1:raise ValueError('exact one new Batch core dependency')
    node=added[0]
    if ({n.tag.rsplit('}',1)[-1] for n in node}!={'groupId','artifactId','version'}
      or len(node)!=3 or node.findtext('{*}version')!='1.17.1'):
        raise ValueError('exact already installed1.17.1 compile, no other fields/exclusions')
    deps.remove(node)
    for root in (old,new):
        for child in root.iter():
            child.text=child.text.strip() if child.text and child.text.strip() else None
            child.tail=None
    if ET.tostring(old)!=ET.tostring(new):raise ValueError('all other Batch POM semantics must remain unchanged')
    return dict(artifact='io.micrometer:micrometer-core',version='1.17.1',scope='compile',
      noOtherSemanticChange=True,noNewExclusions=True,noNewDownload=True)
