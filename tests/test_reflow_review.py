import json,tempfile,threading,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
from PIL import Image
from photocraft_ai.reflow_geometry import visible_bounds,mixed_clusters
from photocraft_ai.reflow_review import validate_review,review_reflow,ReviewPending
from photocraft_ai.backend import Cancelled


class ReviewTests(unittest.TestCase):
    def test_clipped_pixels_do_not_inflate_panel_bounds(self):
        group={'children':[{'kind':'Pixel','clipped':True,'bounds':[-100,-100,500,800]},{'kind':'Shape','bounds':[20,30,100,120]}]}
        self.assertEqual(visible_bounds(group),[20,30,100,120])

    def test_mixed_folder_separates_callout_from_intact_card(self):
        group={'children':[{'kind':'Type','bounds':[0,0,40,20]},{'kind':'Pixel','clipped':True,'bounds':[100,200,400,800]},{'kind':'Shape','bounds':[100,200,100,120]}]}
        clusters=mixed_clusters(group)
        self.assertEqual(clusters[0],([1,2],[100,200,100,120]))
        self.assertEqual(clusters[1],([0],[0,0,40,20]))

    def fixture(self,folder):
        job=Path(folder);info={'width':100,'height':100,'layers':[{'kind':'Type','name':'Title','bounds':[0,0,40,20]}]}
        (job/'reflow-source.json').write_text(json.dumps(info));source=job/'source.png';Image.new('RGB',(100,100),'white').save(source)
        plan=job/'plan.json';current={'placements':[{'key':'u1','x':0,'y':0,'scale':1}]};plan.write_text(json.dumps(current))
        prepared=SimpleNamespace(job=job,source=source,target=object(),layout_options={'width':100,'height':100},prompt='')
        bridge=Mock();bridge.exchange=job
        bridge.client.call.side_effect=lambda method,**kw:Image.new('RGB',(100,100),'white').save(kw['path'])
        service=SimpleNamespace(bridge=bridge,lock=threading.Lock())
        return prepared,service,plan,current

    def test_review_correction_is_rendered_again_and_only_returned_after_approval(self):
        with tempfile.TemporaryDirectory() as folder:
            p,s,path,initial=self.fixture(folder)
            corrected=[{'key':'u1','x':10,'y':10,'scale':1}]
            with patch('photocraft_ai.reflow_review.apply_reflow',return_value=1) as render,patch('photocraft_ai.reflow_review.analyze_json',side_effect=[{'approved':False,'issues':['margin'],'placements':corrected},{'approved':True,'issues':[],'placements':corrected}]):
                result=review_reflow(s,p,path,threading.Event(),lambda _:None)
                self.assertEqual(json.loads(result.read_text())['placements'],corrected)
                self.assertEqual(render.call_count,2)
                self.assertTrue(all(call.kwargs=={'publish':False} for call in render.call_args_list))
                self.assertEqual(s.bridge.client.run.call_count,2)

    def test_approval_cannot_silently_change_unrendered_positions(self):
        unit=[{'key':'u1','bounds':[0,0,40,20]}];current={'placements':[{'key':'u1','x':0,'y':0,'scale':1}]}
        with self.assertRaises(ValueError):validate_review({'approved':True,'issues':[],'placements':[{'key':'u1','x':20,'y':20,'scale':1}]},unit,100,100,current)

    def test_approval_does_not_override_repeated_card_size_guard(self):
        units=[{'key':f'u{i}','bounds':[0,0,20,20],'peer_panel':[20,20]} for i in range(3)]
        plan={'placements':[{'key':f'u{i}','x':0,'y':0,'scale':.1 if i==0 else 1} for i in range(3)]}
        with self.assertRaises(ValueError):validate_review({'approved':True,'issues':[],'placements':plan['placements']},units,100,100,plan)

    def test_card_rows_with_different_heights_still_require_consistent_widths(self):
        units=[{'key':f'u{i}','bounds':[0,0,100,h],'peer_panel':[100,h]} for i,h in enumerate((80,80,100,100,120,120))]
        plan={'placements':[{'key':f'u{i}','x':0,'y':0,'scale':.4 if i==0 else .8} for i in range(6)]}
        with self.assertRaises(ValueError):validate_review({'approved':True,'issues':[],'placements':plan['placements']},units,500,500,plan)

    def test_review_failure_saves_latest_correction_as_pending_draft(self):
        with tempfile.TemporaryDirectory() as folder:
            p,s,path,_=self.fixture(folder)
            responses=[{'approved':False,'issues':['spacing'],'placements':[{'key':'u1','x':i*10,'y':0,'scale':1}]} for i in (1,2,3)]
            with patch('photocraft_ai.reflow_review.apply_reflow',return_value=1) as render,patch('photocraft_ai.reflow_review.analyze_json',side_effect=responses):
                with self.assertRaises(ReviewPending) as caught:review_reflow(s,p,path,threading.Event(),lambda _:None)
                self.assertEqual(render.call_count,4)
                self.assertTrue(all(call.kwargs=={'publish':False} for call in render.call_args_list[:3]))
                saved=render.call_args_list[-1]
                self.assertEqual(saved.kwargs,{'pending':True})
                self.assertEqual(json.loads(saved.args[2].read_text())['placements'],responses[-1]['placements'])
                self.assertEqual(caught.exception.draft_path,1)
                self.assertEqual(json.loads((p.job/'reflow-pending.json').read_text())['status'],'review_required')

    def test_review_service_failure_preserves_rendered_plan(self):
        with tempfile.TemporaryDirectory() as folder:
            p,s,path,_=self.fixture(folder)
            with patch('photocraft_ai.reflow_review.apply_reflow',return_value=1) as render,patch('photocraft_ai.reflow_review.analyze_json',side_effect=TimeoutError('review timeout')):
                with self.assertRaisesRegex(ReviewPending,'review timeout'):review_reflow(s,p,path,threading.Event(),lambda _:None)
                self.assertEqual(render.call_count,2)
                self.assertEqual(render.call_args.args[2],path)
                self.assertEqual(render.call_args.kwargs,{'pending':True})

    def test_initial_render_failure_does_not_publish(self):
        with tempfile.TemporaryDirectory() as folder:
            p,s,path,_=self.fixture(folder)
            with patch('photocraft_ai.reflow_review.apply_reflow',side_effect=ValueError('source changed')) as render:
                with self.assertRaisesRegex(ValueError,'source changed'):review_reflow(s,p,path,threading.Event(),lambda _:None)
                self.assertEqual(render.call_count,1)

    def test_cancellation_during_review_does_not_publish(self):
        with tempfile.TemporaryDirectory() as folder:
            p,s,path,_=self.fixture(folder)
            with patch('photocraft_ai.reflow_review.apply_reflow',return_value=1) as render,patch('photocraft_ai.reflow_review.analyze_json',side_effect=Cancelled('Cancelled')):
                with self.assertRaises(Cancelled):review_reflow(s,p,path,threading.Event(),lambda _:None)
                self.assertEqual(render.call_count,1)

    def test_failed_draft_save_reports_both_errors_without_claiming_success(self):
        with tempfile.TemporaryDirectory() as folder:
            p,s,path,_=self.fixture(folder)
            with patch('photocraft_ai.reflow_review.apply_reflow',side_effect=[1,OSError('disk full')]),patch('photocraft_ai.reflow_review.analyze_json',side_effect=TimeoutError('review timeout')):
                with self.assertRaisesRegex(RuntimeError,'review timeout; could not save.*disk full'):review_reflow(s,p,path,threading.Event(),lambda _:None)
                self.assertFalse((p.job/'reflow-pending.json').exists())

    def test_cancellation_never_renders_or_exports(self):
        with tempfile.TemporaryDirectory() as folder:
            p,s,path,_=self.fixture(folder);cancel=threading.Event();cancel.set()
            with patch('photocraft_ai.reflow_review.apply_reflow') as render:
                with self.assertRaises(Cancelled):review_reflow(s,p,path,cancel,lambda _:None)
                render.assert_not_called()
