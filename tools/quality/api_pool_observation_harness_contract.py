"""Exactly one already installed typed Hikari dependency; every existing harness semantic preserved."""
import xml.etree.ElementTree as ET

def verify_harness(before,after):
    old=ET.fromstring(before);new=ET.fromstring(after)
    old_deps=old.find('{*}dependencies');deps=new.find('{*}dependencies')
    if old_deps is None or deps is None:raise ValueError('both exact original dependency lists')
    selected=lambda n:n.findtext('{*}groupId')=='com.zaxxer' and n.findtext('{*}artifactId')=='HikariCP'
    found=[n for n in deps if selected(n)]
    if any(selected(n) for n in old_deps) or len(found)!=1:raise ValueError('exact one newly declared harness Hikari dependency')
    node=found[0]
    if len(node)!=3 or {n.tag.rsplit('}',1)[-1] for n in node}!={'groupId','artifactId','version'} or node.findtext('{*}version')!='7.1.0':
        raise ValueError('exact existing7.1.0 compile dependency only')
    deps.remove(node)
    for root in (old,new):
        for n in root.iter():
            n.text=n.text.strip() if n.text and n.text.strip() else None
            n.tail=None
    if ET.tostring(old)!=ET.tostring(new):raise ValueError('parent/compiler/ordinary PT/four1.0/static and all other semantics unchanged')
    return dict(added='com.zaxxer:HikariCP:7.1.0',qualitySemanticsUnchanged=True,
      scope='compile',newExclusion=False,newDownload=False)
