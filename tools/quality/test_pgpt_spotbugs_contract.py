"""Independent fixed-policy positive/negative contracts; no JVM, product or classfile IO."""
import unittest
import xml.etree.ElementTree as ET
from pgpt_spotbugs_contract import canonical_plugin, checked_command, FLAGS, NS

XML = '''<project xmlns="http://maven.apache.org/POM/4.0.0"><properties>
<spotbugs.plugin.version>4.10.4.0</spotbugs.plugin.version></properties><build><plugins><plugin>
<artifactId>spotbugs-maven-plugin</artifactId><version>${spotbugs.plugin.version}</version>
<configuration><effort>Max</effort><threshold>Low</threshold><failOnError>true</failOnError>
<xmlOutput>true</xmlOutput></configuration></plugin></plugins></build></project>'''
GOAL = "com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check"


class ContractTest(unittest.TestCase):
    def test_original_property_is_resolved_and_copy_is_independent(self):
        plugin = canonical_plugin(XML)
        self.assertEqual("4.10.4.0", plugin.findtext(NS + "version"))
        plugin.find(NS + "configuration/" + NS + "effort").text = "Min"
        self.assertEqual("Max", canonical_plugin(XML).findtext(NS + "configuration/" + NS + "effort"))

    def test_each_weakened_or_missing_setting_is_rejected(self):
        for old, new in [("Max", "Default"), ("Low", "Medium"),
                         ("<failOnError>true</failOnError>", ""),
                         ("<xmlOutput>true</xmlOutput>", "<xmlOutput>false</xmlOutput>")]:
            with self.subTest(old=old), self.assertRaises(ValueError):
                canonical_plugin(XML.replace(old, new))

    def test_unknown_extra_exclusion_duplicate_or_version_is_rejected(self):
        for text in [XML.replace("</configuration>", "<excludeFilterFile>x</excludeFilterFile></configuration>"),
                     XML.replace("</configuration>", "<effort>Max</effort></configuration>"),
                     XML.replace("4.10.4.0", "4.10.3.0"),
                     XML.replace("</plugins>", ET.tostring(canonical_plugin(XML), encoding="unicode") + "</plugins>"),
                     XML.replace("spotbugs-maven-plugin", "other-plugin")]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                canonical_plugin(text)

    def test_exact_goal_and_flags_are_required(self):
        original = ["mvn", *FLAGS, GOAL]
        self.assertEqual(original, checked_command(original))
        for i in range(len(FLAGS)):
            with self.subTest(i=i), self.assertRaises(ValueError):
                checked_command(["mvn", *FLAGS[:i], *FLAGS[i+1:], GOAL])

    def test_duplicate_conflicting_and_skip_arguments_are_rejected(self):
        for extra in [FLAGS[0], "-Dspotbugs.effort=Min", "-Dspotbugs.skip=true",
                      "-Dspotbugs.excludeFilterFile=anything", "-Dspotbugs.visitors=OnlyOne"]:
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                checked_command(["mvn", *FLAGS, extra, GOAL])

    def test_wrong_goal_and_argument_type_are_rejected(self):
        for command in [["mvn", *FLAGS, GOAL.replace(":check", ":spotbugs")],
                        ["mvn", *FLAGS, GOAL, GOAL], "mvn", [None]]:
            with self.subTest(command=command), self.assertRaises(ValueError):
                checked_command(command)


if __name__ == "__main__":
    unittest.main()
