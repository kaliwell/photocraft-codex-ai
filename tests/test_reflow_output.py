import unittest,tempfile
from pathlib import Path
from photocraft_ai.reflow_output import copy_beside


class OutputTests(unittest.TestCase):
    def test_pending_psd_is_sibling_with_distinct_collision_safe_name(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'project.psd';source.write_bytes(b'original')
            staging=root/'exchange.psd';staging.write_bytes(b'layered PSD')
            approved=copy_beside(staging,source,1500,1500)
            pending=copy_beside(staging,source,1500,1500,pending=True)
            another=copy_beside(staging,source,1500,1500,pending=True)
            self.assertEqual(pending.name,'project_自适应_1500x1500_待审查.psd')
            self.assertEqual(another.name,'project_自适应_1500x1500_待审查_2.psd')
            self.assertEqual(pending.parent,source.parent)
            self.assertEqual(source.read_bytes(),b'original')
            self.assertEqual(approved.read_bytes(),b'layered PSD')

    def test_psb_sibling_keeps_source_and_existing_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'工程.psb';source.write_bytes(b'original')
            staging=root/'exchange.psd';staging.write_bytes(b'new PSD')
            first=copy_beside(staging,source,1500,2000)
            second=copy_beside(staging,source,1500,2000)
            self.assertEqual(first.name,'工程_自适应_1500x2000.psd')
            self.assertEqual(second.name,'工程_自适应_1500x2000_2.psd')
            self.assertEqual(source.read_bytes(),b'original')
            self.assertEqual(first.read_bytes(),b'new PSD')
            self.assertEqual(second.parent,source.parent)

    def test_partial_copy_failure_does_not_leave_a_broken_psd(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'project.psd';source.touch()
            with patch('photocraft_ai.reflow_output.shutil.copyfileobj',side_effect=OSError('disk full')):
                with self.assertRaises(OSError):copy_beside(source,source,100,100)
            self.assertEqual(list(root.glob('*自适应*')),[])
