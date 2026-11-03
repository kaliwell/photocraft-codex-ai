import unittest
from photocraft_ai.localization import english
from photocraft_ai.native import NativeWorker


class LocalizationTests(unittest.TestCase):
    def test_dynamic_progress_and_success_are_canonical_english(self):
        self.assertEqual(english('正在处理生图请求 · 已等待 48 秒'),'Processing image request · waiting 48 s')
        self.assertEqual(english('已生成到新图层 · 本次耗时 12.3 秒 · Ctrl+Z 撤销'),'Added as a new layer · elapsed 12.3 s · Ctrl+Z to undo')

    def test_worker_localizes_messages_without_changing_prompts_or_state(self):
        worker=NativeWorker(None);worker.update(message='选区为空。')
        self.assertEqual(worker.snapshot()['message'],'The selection is empty.')
        self.assertEqual(worker.state['message'],'选区为空。')
        self.assertEqual(english('Unrecognized Codex error'),'Unrecognized Codex error')
