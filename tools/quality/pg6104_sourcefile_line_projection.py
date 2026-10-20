"""Reconcile source-file LINE vs class-family LINE without dropping any uncovered class line."""
from collections import defaultdict
import xml.etree.ElementTree as ET


def sourcefile_lines(tree,module,artifacts):
    owners={}
    for artifact in artifacts:
        if artifact.get('module')==module and artifact['kind']in('JAVA','JAVA_PACKAGE'):
            suffix=artifact['path'].split('/src/main/java/',1)[1]
            if suffix in owners:raise ValueError('one source file one cost owner')
            owners[suffix]=artifact['owner']
    rows=[];seen=set();by_owner=defaultdict(lambda:{'missed':0,'covered':0})
    for package in tree.findall('package'):
        class_counts=defaultdict(lambda:{'missed':0,'covered':0})
        for klass in package.findall('class'):
            counts=next((c for c in klass.findall('counter')if c.get('type')=='LINE'),None)
            if counts is None:continue
            file=klass.get('sourcefilename')
            if not file:raise ValueError('class LINE counter must name its exact source file')
            for key in ('missed','covered'):class_counts[file][key]+=int(counts.get(key))
        for source in package.findall('sourcefile'):
            path=package.get('name')+'/'+source.get('name');key=(module,path)
            if key in seen or path not in owners:raise ValueError('unique current sourcefile with explicit artifact owner')
            seen.add(key)
            counter=next((c for c in source.findall('counter')if c.get('type')=='LINE'),None)
            lines=source.findall('line')
            if counter is None:
                if lines or source.get('name')in class_counts:raise ValueError('explicit LINE counters for executable source files')
                continue
            counts={name:int(counter.get(name))for name in('missed','covered')}
            if min(counts.values())<0 or len({n.get('nr')for n in lines})!=len(lines):raise ValueError('nonnegative counters and unique physical source line numbers')
            independent={'missed':sum(int(n.get('mi'))>0 and int(n.get('ci'))==0 for n in lines),
                         'covered':sum(int(n.get('ci'))>0 for n in lines)}
            if counts!=independent:raise ValueError('sourcefile LINE counter must equal physical instruction-covered line states')
            owner=owners[path]
            for name in('missed','covered'):by_owner[owner][name]+=counts[name]
            rows.append(dict(module=module,sourceFile=path,owner=owner,sourcefileLine=counts,classFamilyLine=dict(class_counts.pop(source.get('name'),{'missed':0,'covered':0}))))
        if class_counts:raise ValueError('every actual class LINE counter has a corresponding sourcefile')
    root=next((c for c in tree.findall('counter')if c.get('type')=='LINE'),None)
    if root is None:raise ValueError('actual module root LINE counter')
    total={name:sum(r['sourcefileLine'][name]for r in rows)for name in('missed','covered')}
    if total!={name:int(root.get(name))for name in('missed','covered')}:raise ValueError('all sourcefile LINE counters equal actual module root')
    return rows,dict(by_owner),total


def projection(manifest,artifacts,root):
    rows=[];owners=defaultdict(lambda:{'missed':0,'covered':0});modules={}
    for module in manifest['modules']:
        name=module['module'];path=root/manifest['coverageRoot']/name/'site/jacoco/jacoco.xml'
        parsed,by_owner,total=sourcefile_lines(ET.parse(path).getroot(),name,artifacts)
        rows.extend(parsed);modules[name]=total
        for owner,counts in by_owner.items():
            for key in('missed','covered'):owners[owner][key]+=counts[key]
    class_total={key:sum(r['classFamilyLine'][key]for r in rows)for key in('missed','covered')}
    source_total={key:sum(r['sourcefileLine'][key]for r in rows)for key in('missed','covered')}
    return dict(sourcefileLineTotals=source_total,classFamilyLineTotals=class_total,sourcefileOwnerLines=dict(owners),
        moduleSourcefileLines=modules,domainDifferences=[r for r in rows if r['classFamilyLine']!=r['sourcefileLine']],
        sourcefileCount=len(rows),noClassMissesRemoved=True,lineCounterDomainsDistinct=True)
