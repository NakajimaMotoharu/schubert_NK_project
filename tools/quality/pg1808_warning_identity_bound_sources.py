"""BUG1172: tool namespaces are not Root UUIDs; frozen1800 remains untouched."""
import re
import pg1800_warning_owned_stop_sources as previous
from pg1772_warning_owned_stop_sources import sources as original_sources

TOOLS='pg1808-warning-owned-stop-tools-v1'
SOURCE=previous.SOURCE
context=previous.context
ORIGINAL_RUN='4148e3e8-f107-431a-ab27-d6e6d1f1772e'
CORRUPTED_RUN='4148e3e8-f107-431a-ab27-d6e6d1f1800e'
UUID=re.compile(r'\b[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}\b')


def namespace(raw):
    return raw.replace('pg1800','pg1808').replace('Pg1800','Pg1808').replace('PG1800','PG1808')


def sources():
    reference=original_sources();result={}
    for name,raw in previous.sources().items():
        raw=raw.replace(CORRUPTED_RUN,ORIGINAL_RUN)
        bound=namespace(raw)
        if UUID.findall(bound)!=UUID.findall(raw):raise ValueError('namespace must preserve every UUID')
        original=name.replace('1800','1772')
        if original in reference:
            old_ids=set(UUID.findall(reference[original]));new_ids=set(UUID.findall(bound))
            added={'9adbf05a-61d0-408b-b51d-ab19c7e5b16a'}if name=='pg1800_native_owned_stop.py'else set()
            if new_ids!=old_ids|added:raise ValueError('all independent original identities required')
        if CORRUPTED_RUN in bound:raise ValueError('corrupted run must not survive')
        if name.endswith('.py'):compile(bound,'<actual identity-bound stop helper>','exec')
        result[namespace(name)]=bound
    return result
