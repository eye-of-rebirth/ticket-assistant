"""接口函数练习。模拟配置由 AI 搭建，核心断言由学习者补充。"""

import unittest
from unittest.mock import patch

from fastapi import HTTPException

with patch("dotenv.load_dotenv"):
    import app


class CloseTicketTests(unittest.TestCase):
    def setUp(self):
        for replacement in (
            patch("app.db.init_db"),
            patch("app.db.close_ticket", return_value=False),
        ):
            replacement.start()
            self.addCleanup(replacement.stop)

    def test_unknown_ticket_raises_404(self):
        with self.assertRaises(HTTPException) as caught:
            app.close_ticket(999999)

        zt = caught.exception.status_code
        sm = caught.exception.detail
        self.assertEqual(zt, 404)
        self.assertEqual(sm, "工单不存在")

    def test_invalid_status_raises_400(self):
        with self.assertRaises(HTTPException) as caught:
            app.get_tickets("abc")

        zt = caught.exception.status_code
        sm = caught.exception.detail

        self.assertEqual(zt, 400)
        self.assertEqual(sm, "工单状态仅支持 open 或 closed")

    def test_blank_suggestion_raises_400(self):
        with patch("app.generate_suggestion") as generate:
            with self.assertRaises(HTTPException) as caught:
                app.suggest(app.TicketCreate(text="   "))

            generate.assert_not_called()

            zt = caught.exception.status_code
            sm = caught.exception.detail

            self.assertEqual(zt, 400)
            self.assertEqual(sm, "工单正文不能为空")


