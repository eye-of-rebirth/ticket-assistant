"""AI编写的回归检查，不代表学习者已独立掌握测试。"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from storage import load_tickets, save_tickets
from service import create_ticket


PROJECT = Path(__file__).resolve().parents[1]


class TicketTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.project = Path(self.directory.name)
        for name in ("main.py", "storage.py","service.py"):
            shutil.copyfile(PROJECT / name, self.project / name)
        self.path = self.project / "tickets.json"
        self.path.write_text("[]\n", encoding="utf-8")

    def cli(self, text):
        result = subprocess.run(
            [sys.executable, str(self.project / "main.py")],
            input=text, text=True, encoding="utf-8", capture_output=True,
            cwd=PROJECT, timeout=5,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def read(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def test_blank_ticket_does_not_change_list(self):
        for text in ("", "   ", "\t\n"):
            with self.subTest(text=repr(text)):
                tickets = [{"id": 3, "text": "已有工单", "status": "closed"}]
                expected = [{"id": 3, "text": "已有工单", "status": "closed"}]
                with self.assertRaises(ValueError):
                    create_ticket(tickets, text)
                self.assertEqual(tickets, expected)

    def test_create_ticket_status(self):
        tickets = []
        first = create_ticket(tickets, "  默认工单  ")
        second = create_ticket(tickets, "关闭工单", status="closed")
        expected = [
            {"id": 1, "text": "默认工单", "status": "open"},
            {"id": 2, "text": "关闭工单", "status": "closed"},
        ]
        self.assertEqual(tickets, expected)
        self.assertEqual(first, expected[0])
        self.assertEqual(second, expected[1])

    def test_invalid_status_does_not_change_list(self):
        for status in ("pending", "", "OPEN", None, 123):
            with self.subTest(status=status):
                tickets = [{"id": 3, "text": "已有工单", "status": "closed"}]
                expected = [{"id": 3, "text": "已有工单", "status": "closed"}]
                with self.assertRaises(ValueError):
                    create_ticket(tickets, "有效内容", status=status)
                self.assertEqual(tickets, expected)

    def test_storage_round_trip(self):
        data = [{"id": 7, "text": "中文工单", "status": "open"}]
        save_tickets(data, self.path)
        self.assertEqual(load_tickets(self.path), data)
        self.assertIn("中文工单", self.path.read_text(encoding="utf-8"))

    def test_missing_file_returns_empty_list(self):
        self.path.unlink()
        self.assertEqual(load_tickets(self.path), [])
        self.assertFalse(self.path.exists())

    def test_malformed_json_is_not_treated_as_empty(self):
        self.path.write_text("{broken", encoding="utf-8")
        with self.assertRaises(json.JSONDecodeError):
            load_tickets(self.path)
        self.assertEqual(self.path.read_text(encoding="utf-8"), "{broken")

    def test_first_start_without_data_file(self):
        self.path.unlink()
        output = self.cli("查看\n首次工单\n退出\n")
        self.assertIn("暂无工单", output)
        self.assertEqual(self.read(), [
            {"id": 1, "text": "首次工单", "status": "open"},
        ])
        self.cli("查看\n退出\n")
        self.assertEqual(self.read(), [
            {"id": 1, "text": "首次工单", "status": "open"},
        ])

    def test_restart_with_id_gaps(self):
        initial = [{"id": 1, "text": "甲", "status": "open"},
                   {"id": 3, "text": "乙", "status": "closed"}]
        self.path.write_text(json.dumps(initial), encoding="utf-8")
        self.cli("投影仪无法启动\n退出\n")
        self.cli("门打不开\n退出\n")
        self.assertEqual(self.read(), initial + [
            {"id": 4, "text": "投影仪无法启动", "status": "open"},
            {"id": 5, "text": "门打不开", "status": "open"},
        ])

    def test_empty_and_whitespace(self):
        output = self.cli("   \n\t\n 查看 \n 退出 \n")
        self.assertEqual(output.count("问题不能为空"), 2)
        self.assertIn("暂无工单", output)
        self.assertIn("再见", output)
        self.assertEqual(self.read(), [])

    def test_create_then_view(self):
        output = self.cli("新问题\n查看\n退出\n")
        self.assertEqual(self.read(), [{"id": 1, "text": "新问题", "status": "open"}])
        self.assertIn("固定建议", output)
        self.assertIn("'text': '新问题'", output)

    def test_view_does_not_write(self):
        data = [{"id": 2, "text": "甲", "status": "open"},
                {"id": 8, "text": "乙", "status": "closed"}]
        self.path.write_text(json.dumps(data), encoding="utf-8")
        before = self.path.read_bytes()
        output = self.cli("查看\n退出\n")
        self.assertTrue(any("甲" in line and "乙" not in line for line in output.splitlines()))
        self.assertTrue(any("乙" in line and "甲" not in line for line in output.splitlines()))
        self.assertEqual(self.path.read_bytes(), before)

    def test_import_does_not_start_cli(self):
        self.path.unlink()
        result = subprocess.run(
            [sys.executable, "-c", "import main"], cwd=self.project,
            input="", text=True, capture_output=True, timeout=5,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertFalse(self.path.exists())
