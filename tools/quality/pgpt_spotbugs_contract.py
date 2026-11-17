"""BUG3188/YKT2656: bind a safe subset to the existing module quality settings.

Pure XML/command validation only; this module never launches a process or grants
permission to read a classfile. Caller source/byte/authority guards still apply.
"""
import copy
import xml.etree.ElementTree as ET

NS = "{http://maven.apache.org/POM/4.0.0}"
VERSION = "4.10.4.0"
SETTINGS = {"effort": "Max", "threshold": "Low", "failOnError": "true", "xmlOutput": "true"}
FLAGS = tuple(f"-Dspotbugs.{key}={value}" for key, value in SETTINGS.items())


def canonical_plugin(module_xml):
    """Copy only an exactly recognized original module plugin, without weakening it."""
    root = ET.fromstring(module_xml)
    plugins = [p for p in root.findall(".//" + NS + "plugin")
               if p.findtext(NS + "artifactId") == "spotbugs-maven-plugin"]
    if len(plugins) != 1:
        raise ValueError("exactly one original SpotBugs plugin required")
    plugin = copy.deepcopy(plugins[0])
    version = plugin.find(NS + "version")
    if version is None:
        raise ValueError("explicit plugin version required")
    declared = version.text
    if declared and declared.startswith("${") and declared.endswith("}"):
        declared = root.findtext(NS + "properties/" + NS + declared[2:-1])
    if declared != VERSION:
        raise ValueError("original SpotBugs version changed")
    version.text = declared
    config = plugin.find(NS + "configuration")
    if config is None or len(config) != 4 or {n.tag.removeprefix(NS): n.text for n in config} != SETTINGS:
        raise ValueError("exact original Max/Low/failOnError/xmlOutput contract required")
    return plugin


def checked_command(command):
    """Validate explicit runtime properties in addition to the bound POM settings."""
    if not isinstance(command, list) or any(not isinstance(v, str) for v in command):
        raise ValueError("explicit argument vector required")
    for key, expected in SETTINGS.items():
        values = [v for v in command if v.startswith("-Dspotbugs." + key + "=")]
        if values != [f"-Dspotbugs.{key}={expected}"]:
            raise ValueError("missing, duplicate or altered SpotBugs property: " + key)
    if command.count("com.github.spotbugs:spotbugs-maven-plugin:" + VERSION + ":check") != 1:
        raise ValueError("explicit original plugin goal required")
    if any(any(word in v.lower() for word in ("excludefilter", "visitors=", "spotbugs.skip"))
           for v in command):
        raise ValueError("no exclusion, visitor selection or skipped analysis")
    return list(command)
