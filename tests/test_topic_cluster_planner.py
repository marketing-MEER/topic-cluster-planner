import tempfile
import unittest
from pathlib import Path

import pandas as pd
from click.testing import CliRunner

from topic_cluster_planner import cli, core

EXAMPLES = Path(__file__).parent.parent / "examples"


def kws(pairs):
    return pd.DataFrame(pairs, columns=["keyword", "volume"])


class TreeTest(unittest.TestCase):
    def test_tokens(self):
        self.assertEqual(core.tokens("How to make Cold Brews"), frozenset({"cold", "brew"}))

    def test_most_specific_parent(self):
        tree = core.build_tree(kws([("cold brew", 100), ("cold brew ratio", 50), ("cold brew concentrate ratio", 10),
                                    ("moka pot", 80)]))
        self.assertIsNone(tree["cold brew"])
        self.assertEqual(tree["cold brew ratio"], "cold brew")
        self.assertEqual(tree["cold brew concentrate ratio"], "cold brew ratio")
        self.assertIsNone(tree["moka pot"])


class PlanTest(unittest.TestCase):
    def setUp(self):
        self.p = core.plan(kws([("cold brew", 100), ("how to make cold brew", 60), ("cold brew ratio", 50),
                                ("cold brew concentrate ratio", 10), ("moka pot", 80), ("moka pot size", 5)]))
        self.role = dict(zip(self.p["keyword"], self.p["role"]))
        self.page = dict(zip(self.p["keyword"], self.p["page"]))

    def test_roles_and_pages(self):
        self.assertEqual(self.role["cold brew"], "pillar")
        self.assertEqual(self.role["cold brew ratio"], "spoke")
        self.assertEqual(self.role["cold brew concentrate ratio"], "section")
        self.assertEqual(self.page["cold brew concentrate ratio"], "/cold-brew-ratio/")
        # one child only: too small for a cluster
        self.assertEqual(self.role["moka pot"], "standalone")
        self.assertEqual((self.role["moka pot size"], self.page["moka pot size"]), ("section", "/moka-pot/"))

    def test_clusters_and_links(self):
        cl = core.clusters(self.p).set_index("cluster")
        self.assertEqual(cl.at["cold brew", "spokes"], 2)
        self.assertEqual(cl.at["moka pot", "type"], "standalone page")
        links = core.link_plan(self.p)
        self.assertIn(("/cold-brew/", "/cold-brew-ratio/"), set(zip(links["from_page"], links["to_page"])))
        self.assertIn(("/cold-brew-ratio/", "/cold-brew/"), set(zip(links["from_page"], links["to_page"])))
        self.assertFalse((links["cluster"] == "moka pot").any())

    def test_empty(self):
        p = core.plan(kws([]))
        self.assertTrue(p.empty)
        self.assertTrue(core.clusters(p).empty)
        self.assertTrue(core.link_plan(p).empty)


class CliTest(unittest.TestCase):
    def test_example_writes_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "t"
            res = CliRunner().invoke(cli.main, [str(EXAMPLES / "coffee_keywords.csv"), "-o", str(out)])
            self.assertEqual(res.exit_code, 0, res.output)
            self.assertIn("Topic cluster plan", out.with_suffix(".html").read_text(encoding="utf-8"))
            self.assertTrue(out.with_suffix(".xlsx").exists())


if __name__ == "__main__":
    unittest.main()
