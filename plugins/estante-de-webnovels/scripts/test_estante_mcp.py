import json
import os
import tempfile
import unittest
from pathlib import Path

os.environ["ESTANTE_DATA_DIR"] = tempfile.mkdtemp(prefix="estante-test-")
import estante_mcp as app


class StorageTests(unittest.TestCase):
    def test_original_is_preserved_across_two_profiles(self):
        original = {"kind": "original", "text": "Lia abriu a porta. Caio ficou na sala."}
        app.call("save_work", {"work_id": "cena", "work": original})
        app.call("save_work", {"work_id": "cena", "work": {"kind": "version", "profile": "Obra A", "text": "Lia abriu a porta.\n\nCaio ficou na sala."}})
        app.call("save_work", {"work_id": "cena", "work": {"kind": "version", "profile": "Obra B", "text": "A porta se abriu sob a mao de Lia; Caio, ainda na sala, esperou."}})
        saved = app.call("get_work", {"work_id": "cena"})
        self.assertEqual(saved["original"], original)
        self.assertEqual([v["profile"] for v in saved["versions"]], ["Obra A", "Obra B"])
        self.assertNotEqual(saved["versions"][0]["text"], saved["versions"][1]["text"])

    def test_profile_sources_and_inaccessible_source_are_recorded(self):
        profile = {"status": "parcial", "sources": [{"url": "https://example.invalid/chapter", "access": "inacessivel", "reason": "login necessario"}], "evidence": []}
        app.call("save_profile", {"title": "Shadow Slave", "profile": profile})
        self.assertEqual(app.call("get_profile", {"title": "Shadow Slave"})["sources"][0]["access"], "inacessivel")

    def test_protocol_lists_tools(self):
        answer = app.response({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        names = {tool["name"] for tool in answer["result"]["tools"]}
        self.assertIn("save_work", names)
        self.assertIn("set_reading_progress", names)


if __name__ == "__main__":
    unittest.main()
