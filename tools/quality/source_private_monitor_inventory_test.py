"""Independent source fixtures for exclusive private-monitor symbol inventory; no Main execution."""
import subprocess
import tempfile
import unittest
from pathlib import Path
from pg5540_snapshot_scratch_selected import ROOT, TC

FIELD = ('path', 'owner', 'name', 'typeStart', 'typeEnd', 'initStart', 'initEnd', 'blockCount', 'otherReads', 'eligible')
BLOCK = ('path', 'fieldOwner', 'name', 'start', 'end', 'bodyStart', 'bodyEnd', 'expressionStart', 'expressionEnd', 'blockOwner', 'method')


def facts(text):
    fields, blocks = [], []
    for line in text.splitlines():
        if not line:
            continue
        values = line.split('\t'); kind = values.pop(0)
        names = FIELD if kind == 'MONITOR_FIELD' else BLOCK if kind == 'MONITOR_BLOCK' else None
        if names is None or len(values) != len(names):
            raise ValueError('only complete private-monitor fact rows')
        row = dict(zip(names, values))
        for key in ('typeStart', 'typeEnd', 'initStart', 'initEnd', 'blockCount', 'otherReads') if kind == 'MONITOR_FIELD' else ('start', 'end', 'bodyStart', 'bodyEnd', 'expressionStart', 'expressionEnd'):
            if not row[key].isdigit():
                raise ValueError('actual nonnegative source offsets/counts')
            row[key] = int(row[key])
        if kind == 'MONITOR_FIELD':
            if row['eligible'] not in ('true', 'false'):
                raise ValueError('explicit eligible predicate')
            row['eligible'] = row['eligible'] == 'true'; fields.append(row)
        else:
            blocks.append(row)
    index = {(r['path'], r['owner'], r['name']): r for r in fields}
    if len(index) != len(fields):
        raise ValueError('unique resolved private field symbol')
    seen = set()
    for row in blocks:
        ident = (row['path'], row['fieldOwner'], row['name'])
        if ident not in index or not index[ident]['eligible'] or (row['path'], row['start']) in seen:
            raise ValueError('one eligible field and unique block source span')
        seen.add((row['path'], row['start']))
    for ident, row in index.items():
        if row['eligible'] and (row['otherReads'] != 0 or row['blockCount'] != sum((b['path'], b['fieldOwner'], b['name']) == ident for b in blocks)):
            raise ValueError('every eligible field reference is exactly a monitor block')
    return {'fields': fields, 'blocks': blocks}


class PrivateMonitorSymbolsTest(unittest.TestCase):
    def test_owned_only_monitors_and_alias_wait_qualified_and_factory_rejection(self):
        fixture = '''package fixture;
final class Example {
  private final Object lock = new Object();
  private final Object alias = new Object();
  private final Object waiting = new Object();
  private final Object qualified = new Object();
  private final Object supplied;
  private Object mutable = new Object();
  Example(Object input) { supplied = input; }
  int read() { synchronized(lock) { return 1; } }
  void write() { synchronized(this.lock) { read(); } }
  final class Nested { void call() { synchronized(lock) {} } }
  Object escape() { synchronized(alias) {} return alias; }
  void waitOnce() throws InterruptedException { synchronized(waiting) { waiting.wait(1); } }
  void foreign(Example other) { synchronized(other.qualified) {} }
  void imported() { synchronized(supplied) {} synchronized(mutable) {} }
}
'''
        with tempfile.TemporaryDirectory(prefix='pgpt-monitor-symbols-') as temp:
            root = Path(temp); classes = root/'classes'; classes.mkdir(); sources = root/'input'; sources.mkdir()
            path = sources/'Example.java'; path.write_text(fixture)
            helper = ROOT/'tools/quality/SourcePrivateMonitorInventory.java'
            subprocess.run([str(TC/'jdk-25.0.4/bin/javac'), '--release', '25', '-Xlint:all', '-Werror', '-d', str(classes), str(helper)], check=True, capture_output=True)
            result = subprocess.run([str(TC/'jdk-25.0.4/bin/java'), '-cp', str(classes), 'SourcePrivateMonitorInventory', str(sources), str(classes)], check=True, capture_output=True, text=True)
            value = facts(result.stdout)
            self.assertEqual({'lock'}, {r['name'] for r in value['fields'] if r['eligible']})
            self.assertEqual(3, len(value['blocks']))
            self.assertEqual({'alias', 'waiting', 'qualified'}, {r['name'] for r in value['fields'] if not r['eligible']})
            self.assertNotIn('supplied', {r['name'] for r in value['fields']})
            self.assertNotIn('mutable', {r['name'] for r in value['fields']})
            self.assertTrue(any(r['blockOwner'].endswith('$Nested') for r in value['blocks']))
            for row in value['blocks']:
                self.assertTrue(fixture[row['start']:row['end']].startswith('synchronized'))
                self.assertEqual('{', fixture[row['bodyStart']]); self.assertEqual('}', fixture[row['bodyEnd']-1])
                self.assertIn(fixture[row['expressionStart']:row['expressionEnd']], ('lock', 'this.lock'))

    def test_malformed_or_duplicate_rows_are_not_facts(self):
        for value in ('UNKNOWN\tx', 'MONITOR_FIELD\tx', 'MONITOR_BLOCK\tx'):
            with self.assertRaises(ValueError):
                facts(value)


if __name__ == '__main__':
    unittest.main()
