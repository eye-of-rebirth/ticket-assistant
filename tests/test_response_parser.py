"""AI编写的模型响应解析回归；不调用模型。"""

import json
import unittest

from response_parser import parse_response


class ResponseParserTests(unittest.TestCase):
    def test_non_string_input_is_rejected(self):
        for raw in (None, {}, [], 123, True, b"{}"):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError) as caught:
                    parse_response(raw)
                self.assertIn("字符串", str(caught.exception))

    def test_complete_object(self):
        expected = {
            "category": "设备故障",
            "summary": "投影仪无法启动",
            "suggestion": "检查电源连接",
        }
        self.assertEqual(parse_response(json.dumps(expected)), expected)

    def test_each_required_field_is_checked(self):
        complete = {"category": "设备故障", "summary": "故障摘要", "suggestion": "排查建议"}
        for missing in complete:
            with self.subTest(missing=missing):
                sample = {key: value for key, value in complete.items() if key != missing}
                with self.assertRaises(ValueError) as caught:
                    parse_response(json.dumps(sample))
                self.assertIn(missing, str(caught.exception))

    def test_non_object_json_is_rejected(self):
        for raw in ("[]", "null", "123", '"hello"', "true"):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    parse_response(raw)

    def test_invalid_json_is_rejected(self):
        for raw in ("不是JSON", "{broken", ""):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    parse_response(raw)

    def test_all_fields_are_trimmed(self):
        expected = {"category": "设备故障", "summary": "投影仪无法启动", "suggestion": "检查电源"}
        padded = {key: " \t" + value + "\n " for key, value in expected.items()}
        self.assertEqual(parse_response(json.dumps(padded)), expected)

    def test_wrong_field_types_are_rejected(self):
        complete = {"category": "设备故障", "summary": "故障摘要", "suggestion": "排查建议"}
        for field in complete:
            for invalid in (123, None, [], {}, True):
                with self.subTest(field=field, invalid=invalid):
                    sample = {**complete, field: invalid}
                    with self.assertRaises(ValueError) as caught:
                        parse_response(json.dumps(sample))
                    self.assertIn(field, str(caught.exception))

    def test_blank_fields_are_rejected(self):
        complete = {"category": "设备故障", "summary": "故障摘要", "suggestion": "排查建议"}
        for field in complete:
            for invalid in ("", "   ", "\t\n"):
                with self.subTest(field=field, invalid=invalid):
                    sample = {**complete, field: invalid}
                    with self.assertRaises(ValueError) as caught:
                        parse_response(json.dumps(sample))
                    self.assertIn(field, str(caught.exception))

    def test_summary_length_boundary(self):
        for length in (79, 80, 81):
            with self.subTest(length=length):
                sample = {"category": "设备故障", "summary": "中" * length, "suggestion": "检查电源"}
                if length <= 80:
                    self.assertEqual(parse_response(json.dumps(sample)), sample)
                else:
                    with self.assertRaises(ValueError) as caught:
                        parse_response(json.dumps(sample))
                    self.assertIn("summary", str(caught.exception))
                    self.assertIn("80", str(caught.exception))

    def test_summary_limit_uses_trimmed_length(self):
        sample = {"category": "设备故障", "summary": " \t" + "中" * 80 + "\n ", "suggestion": "检查电源"}
        self.assertEqual(parse_response(json.dumps(sample))["summary"], "中" * 80)

    def test_summary_limit_does_not_limit_other_fields(self):
        sample = {"category": "类" * 81, "summary": "简短摘要", "suggestion": "议" * 81}
        self.assertEqual(parse_response(json.dumps(sample)), sample)
