"""Generated PPTX regression checks for V9 table borders and column geometry."""
import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}

class TableOutputTest(unittest.TestCase):
    def build(self, widths):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        scene = Path(folder.name) / "scene.json"
        output = Path(folder.name) / "deck.pptx"
        scene.write_text(json.dumps({"width":1280,"height":720,"slides":[{"title":"Comparison","notes":"Test","elements":[{"type":"table","x":56,"y":230,"w":1168,"h":240,"colWidths":widths,"rows":[["Metric","Before","After"],["Time","16","9"]]}]}]}))
        completed = subprocess.run(["node",str(ROOT/"scripts/build_deck.cjs"),str(scene),str(output)],capture_output=True,text=True)
        return completed, output

    def test_editable_table_has_no_vertical_borders_and_keeps_column_widths(self):
        completed, output = self.build([268,450,450])
        self.assertEqual(completed.returncode,0,completed.stderr)
        with zipfile.ZipFile(output) as archive:
            slide = ET.fromstring(archive.read("ppt/slides/slide1.xml"))
        table = slide.find(".//a:tbl",NS)
        self.assertIsNotNone(table)
        widths=[int(c.get("w")) for c in table.findall("a:tblGrid/a:gridCol",NS)]
        self.assertEqual(widths,[round(w*9525) for w in [268,450,450]])
        for cell in table.findall(".//a:tc",NS):
            for side in ["lnL","lnR"]:
                self.assertIsNotNone(cell.find("a:tcPr/a:"+side+"/a:noFill",NS))
        self.assertEqual([t.text for t in table.findall(".//a:t",NS)],["Metric","Before","After","Time","16","9"])

    def test_invalid_column_geometry_is_rejected(self):
        completed, _ = self.build([100,100,100])
        self.assertNotEqual(completed.returncode,0)
        self.assertIn("colWidths",completed.stderr)

if __name__ == "__main__":
    unittest.main()
