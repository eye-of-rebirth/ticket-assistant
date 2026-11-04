"""AI编写的回归检查，不代表学习者已独立掌握测试。"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
from openai import APIError, APITimeoutError

fake_llm = types.ModuleType("llm_client")
fake_llm.generate_suggestion = lambda text: {
    "category": "设备故障", "summary": text, "suggestion": "模拟建议：" + text,
}
with patch.dict(sys.modules, {"llm_client": fake_llm}):
    import main
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
        (self.project / "llm_client.py").write_text(
            'def generate_suggestion(text):\n'
            '    return {"category": "设备故障", "summary": text, "suggestion": "模拟建议：" + text}\n',
            encoding="utf-8",
        )
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

    def test_cli_reports_malformed_json_without_overwriting(self):
        original = b"{broken JSON"
        self.path.write_bytes(original)
        output = self.cli("")
        self.assertIn("工单文件格式损坏", output)
        self.assertIn("tickets.json", output)
        self.assertNotIn("请输入问题", output)
        self.assertEqual(self.path.read_bytes(), original)

    def test_read_permission_error_stops_before_input_or_save(self):
        with patch.object(main, "load_tickets", side_effect=PermissionError("denied")), \
                patch("builtins.input") as read_input, \
                patch.object(main, "save_tickets") as save, \
                patch("builtins.print") as output:
            main.main()
        read_input.assert_not_called()
        save.assert_not_called()
        output.assert_any_call("没有权限读取工单文件")

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
        self.assertIn("模拟建议：新问题", output)
        self.assertIn("分类:设备故障", output)
        self.assertIn("摘要:新问题", output)
        self.assertIn("建议:模拟建议：新问题", output)
        self.assertIn("'text': '新问题'", output)

    def test_ticket_is_saved_before_suggestion(self):
        expected = [{"id": 1, "text": "新问题", "status": "open"}]

        def generate(text):
            self.assertEqual(text, "新问题")
            self.assertEqual(self.read(), expected)
            return {"category": "设备故障", "summary": "新问题", "suggestion": "模拟建议"}

        with patch.object(main, "__file__", str(self.project / "main.py")), \
                patch.object(main, "generate_suggestion", side_effect=generate) as suggest, \
                patch("builtins.input", side_effect=["新问题", "查看", "退出"]), \
                patch("builtins.print") as output:
            main.main()
        suggest.assert_called_once_with("新问题")
        output.assert_any_call("建议:模拟建议")
        self.assertEqual(self.read(), expected)

    def test_api_failure_keeps_saved_ticket_and_loop_running(self):
        cases = [
            (APITimeoutError(request=object()), "工单已保存，建议生成超时"),
            (APIError("simulated failure", request=object(), body=None),
             "工单已保存，建议生成失败，请稍后再试"),
            (ValueError("invalid model response"),
             "工单已保存，建议生成失败：invalid model response"),
        ]
        for error, message in cases:
            with self.subTest(error=type(error).__name__):
                self.path.write_text("[]", encoding="utf-8")
                with patch.object(main, "__file__", str(self.project / "main.py")), \
                        patch.object(main, "generate_suggestion", side_effect=[error, {
                            "category": "设备故障", "summary": "第二条", "suggestion": "下一次建议",
                        }]) as suggest, \
                        patch("builtins.input", side_effect=["第一条", "查看", "第二条", "退出"]), \
                        patch("builtins.print") as output:
                    main.main()
                output.assert_any_call(message)
                output.assert_any_call("建议:下一次建议")
                self.assertEqual(suggest.call_count, 2)
                self.assertEqual(self.read(), [
                    {"id": 1, "text": "第一条", "status": "open"},
                    {"id": 2, "text": "第二条", "status": "open"},
                ])

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
