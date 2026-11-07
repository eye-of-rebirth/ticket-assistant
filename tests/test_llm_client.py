"""AI编写的客户端回归；使用假密钥和模拟SDK，不读取真实.env或请求API。"""

import importlib.util
import io
import json
import os
from pathlib import Path
import runpy
import sys
import tempfile
from types import SimpleNamespace
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
from openai import APITimeoutError


PROJECT = Path(__file__).resolve().parents[1]


class LlmClientTests(unittest.TestCase):
    def setUp(self):
        for replacement in (
            patch("dotenv.load_dotenv"),
            patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-placeholder"}, clear=True),
        ):
            replacement.start()
            self.addCleanup(replacement.stop)
        sdk_patch = patch("openai.OpenAI")
        self.factory = sdk_patch.start()
        self.addCleanup(sdk_patch.stop)
        spec = importlib.util.spec_from_file_location("checked_llm_client", PROJECT / "llm_client.py")
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.expected = {"category": "设备故障", "summary": "简短摘要", "suggestion": "检查电源"}
        self.factory.return_value.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(self.expected)))],
        )

    def test_missing_key_is_checked_only_when_called(self):
        self.factory.assert_not_called()
        del os.environ["DEEPSEEK_API_KEY"]
        with self.assertRaises(ValueError) as caught:
            self.module.generate_suggestion("投影仪打不开")
        self.assertIn("DEEPSEEK_API_KEY", str(caught.exception))
        self.factory.assert_not_called()

    def test_configured_client_returns_validated_dictionary(self):
        self.assertEqual(self.module.generate_suggestion("投影仪打不开"), self.expected)
        self.factory.assert_called_once_with(
            api_key="test-placeholder", base_url="https://api.deepseek.com",
            timeout=30.0, max_retries=0,
        )
        request = self.factory.return_value.chat.completions.create.call_args.kwargs
        self.assertIn("投影仪打不开", request["messages"][1]["content"])

    def test_direct_script_entry_has_no_scope_error(self):
        output = io.StringIO()
        with redirect_stdout(output):
            runpy.run_path(str(PROJECT / "llm_client.py"), run_name="__main__")
        self.factory.return_value.chat.completions.create.assert_called_once()
        self.assertIn("检查电源", output.getvalue())

    def test_cli_without_key_saves_ticket_and_keeps_running(self):
        del os.environ["DEEPSEEK_API_KEY"]
        with patch.dict(sys.modules, {"llm_client": self.module}):
            spec = importlib.util.spec_from_file_location("checked_main", PROJECT / "main.py")
            cli = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cli)
        with tempfile.TemporaryDirectory(dir=PROJECT.parent / ".skill-validation-deps") as folder:
            path = Path(folder) / "tickets.json"
            with patch.object(cli, "__file__", str(Path(folder) / "main.py")), \
                    patch("builtins.input", side_effect=["查看", "新问题", "查看", "退出"]) as read, \
                    patch("builtins.print") as output:
                cli.main()
            self.assertEqual(read.call_count, 4)
            output.assert_any_call("工单已保存，建议生成失败：未配置DEEPSEEK_API_KEY")
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), [
                {"id": 1, "text": "新问题", "status": "open"},
            ])
        self.factory.assert_not_called()

    def test_missing_summary_is_rejected(self):
        sample = {
            "category": "设备故障",
            "suggestion": "检查电源",
        }
        reply = self.factory.return_value.chat.completions.create.return_value
        reply.choices[0].message.content = json.dumps(sample)

        with self.assertRaises(ValueError) as caught:
            self.module.generate_suggestion("投影仪打不开")

        self.assertIn("summary", str(caught.exception))

    def test_numeric_summary_is_rejected(self):
        sample = {
            "category": "设备故障",
            "summary":123,
            "suggestion": "检查电源",
        }
        reply = self.factory.return_value.chat.completions.create.return_value
        reply.choices[0].message.content = json.dumps(sample)

        with self.assertRaises(ValueError) as caught:
            self.module.generate_suggestion("投影仪打不开")

        self.assertIn("summary", str(caught.exception))
        self.assertIn("字符串", str(caught.exception))

    def test_two_timeouts_are_propagated_without_third_request(self):
        #假sdk(软件包)抛出超时错误
        create = self.factory.return_value.chat.completions.create
        create.side_effect = APITimeoutError(request=object())
        #断言时错误
        with self.assertRaises(APITimeoutError) as caught:
            self.module.generate_suggestion("投影仪打不开")
        # 首次超时后只重试一次
        self.assertEqual(create.call_count, 2)

    def test_timeout_then_success_returns_validated_result(self):
        create = self.factory.return_value.chat.completions.create
        create.side_effect = [APITimeoutError(request=object()), create.return_value]

        result = self.module.generate_suggestion("投影仪打不开")

        self.assertEqual(result, self.expected)
        self.assertEqual(create.call_count, 2)

    def test_long_summary_is_rejected(self):
        sample = {
            "category": "设备故障",
            "summary":  "中" * 81,
            "suggestion": "检查电源",
        }
        reply = self.factory.return_value.chat.completions.create.return_value
        reply.choices[0].message.content = json.dumps(sample)

        with self.assertRaises(ValueError) as caught:
            self.module.generate_suggestion("投影仪打不开")

        self.assertIn("summary", str(caught.exception))
        self.assertIn("80", str(caught.exception))

        self.factory.return_value.chat.completions.create.assert_called_once()
