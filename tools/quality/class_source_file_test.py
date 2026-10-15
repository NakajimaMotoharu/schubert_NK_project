from pathlib import Path
import subprocess
import tempfile
import unittest
from class_source_file import source_file
from source_import_expansion_test import JDK


class SourceFile(unittest.TestCase):
    def test_real_java25_modified_utf8_inner_class_and_framing_negative(self):
        with tempfile.TemporaryDirectory(prefix='pgpt-sourcefile-')as d:
            p=Path(d);(p/'Subject.java').write_text('class Subject {String label="\\u0000😀"; class Inner {}}')
            subprocess.run([str(JDK/'javac'),'-g',str(p/'Subject.java')],capture_output=True,check=True,timeout=30)
            for n in ['Subject.class','Subject$Inner.class']:
                raw=(p/n).read_bytes();self.assertEqual('Subject.java',source_file(raw))
                for bad in [raw[:-1],raw+b'x',b'BAD!'+raw[4:],raw[:15],raw.replace(b'Subject.java',b'../hack.java')]:
                    with self.assertRaises(ValueError):source_file(bad)
            with self.assertRaises(ValueError):source_file(bytearray(raw))


if __name__=='__main__':unittest.main()
