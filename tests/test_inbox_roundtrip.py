import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIX6 = os.path.join(ROOT, "runtime", "scripts", "six6.py")
FARM = os.path.join(ROOT, "skill-topic-lab", "scripts", "farm.py")
INBOX = os.path.join(ROOT, "skill-autoloop", "scripts", "process_inbox.py")


def run(*args):
    return subprocess.run([sys.executable, *args], capture_output=True, text=True)


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def make_seed(seed_id, maturity):
    return {"id": seed_id, "topic": "t", "description": "d", "source": "s",
            "maturity": maturity, "created_at": "2026-04-04T00:00:00"}


class TempBase(unittest.TestCase):
    def setUp(self):
        self.base = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.base, True)
        self.assertEqual(run(SIX6, "init", "--base-dir", self.base).returncode, 0)
        self.inbox = os.path.join(self.base, "data", "inbox.jsonl")
        self.seeds = os.path.join(self.base, "data", "topic-lab-seeds.jsonl")


class InboxRoundtrip(TempBase):
    def test_water_event_not_lost(self):
        write_jsonl(self.seeds, [make_seed("s1", 20)])
        write_jsonl(self.inbox, [{"type": "topic-lab-water", "seed_id": "s1", "ts": 1}])
        r = run(INBOX, "--base-dir", self.base)
        self.assertEqual(r.returncode, 0, r.stderr)
        rows = read_jsonl(self.inbox)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["event"], "seed-watered")
        self.assertEqual(read_jsonl(self.seeds)[0]["maturity"], 30)

    def test_plain_item_cleared(self):
        write_jsonl(self.inbox, [{"type": "x-todo", "msg": "hi", "ts": 1}])
        self.assertEqual(run(INBOX, "--base-dir", self.base).returncode, 0)
        self.assertEqual(read_jsonl(self.inbox), [])

    def test_failed_item_retained_and_deadlettered(self):
        write_jsonl(self.inbox, [{"type": "topic-lab-water", "ts": 1}])
        run(INBOX, "--base-dir", self.base)
        self.assertEqual(len(read_jsonl(self.inbox)), 1)
        dl = os.path.join(self.base, "deadletter", "inbox-deadletter.jsonl")
        self.assertEqual(len(read_jsonl(dl)), 1)


class FarmTick(TempBase):
    def test_decay_keeps_active(self):
        write_jsonl(self.seeds, [make_seed("a", 30)])
        self.assertEqual(run(FARM, "--base-dir", self.base, "--tick").returncode, 0)
        seed = read_jsonl(self.seeds)[0]
        self.assertEqual(seed["maturity"], 25)
        self.assertEqual(seed.get("status", "active"), "active")

    def test_compost_at_zero(self):
        write_jsonl(self.seeds, [make_seed("b", 5)])
        run(FARM, "--base-dir", self.base, "--tick")
        seed = read_jsonl(self.seeds)[0]
        self.assertEqual(seed["maturity"], 0)
        self.assertEqual(seed["status"], "composted")
        self.assertEqual(read_jsonl(self.inbox)[-1]["event"], "seed-composted")


class DemoValidate(unittest.TestCase):
    def test_demo_validates(self):
        self.assertEqual(run(SIX6, "validate", "--base-dir", os.path.join(ROOT, "demo")).returncode, 0)


if __name__ == "__main__":
    unittest.main()
