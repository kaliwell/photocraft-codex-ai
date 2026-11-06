import unittest
from unittest.mock import Mock
from photocraft_ai.layout import validate_layout, validate_options, build_layout
from pathlib import Path
import tempfile, json
from photocraft_ai.bridge import PhotoCraftBridge


class LayoutTests(unittest.TestCase):
    def test_model_font_style_alias_is_normalized_without_mutating_response(self):
        text={'kind':'text','x':20,'y':80,'text':'Title','font_style':'Regular'}
        value={'width':600,'height':1200,'background':'#ffffff','elements':[text]}
        normalized=validate_layout(value)
        self.assertEqual(normalized['elements'][0]['fontStyle'],'Regular')
        self.assertNotIn('font_style',normalized['elements'][0])
        self.assertIn('font_style',text)
        text['fontStyle']='Bold'
        with self.assertRaisesRegex(ValueError,'Conflicting layout font styles'):validate_layout(value)

    def test_unknown_fields_are_reported_and_not_silently_discarded(self):
        value={'width':600,'height':1200,'background':'#ffffff','elements':[{'kind':'text','x':20,'y':80,'text':'Title','command':'execute'}]}
        with self.assertRaisesRegex(ValueError,'Unsupported layout fields: command'):validate_layout(value)

    def test_parameters_reject_invalid_dimensions_fonts_and_dpi(self):
        self.assertEqual(validate_options()['dpi'],72)
        for options in [{'width':True},{'height':0},{'width':8192,'height':8192},{'dpi':0},{'font':'bad\nfont'},{'font_style':'bad\nstyle'},{'reference_size':1},{'command':'run'}]:
            with self.assertRaises(ValueError):validate_options(options)

    def test_dpi_keeps_pixel_font_size_and_sets_document_resolution(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);path=root/'layout.json'
            path.write_text(json.dumps({'width':600,'height':1200,'dpi':300,'background':'#ffffff','elements':[{'kind':'text','x':20,'y':80,'text':'Title','size':100,'font':'Arial'}]}))
            bridge=Mock();bridge.exchange=root
            build_layout(bridge,path,root)
            bridge.client.run.assert_any_call('file.new',width=600,height=1200,resolution=300)
            bridge.client.run.assert_any_call('type.create',x=20,y=80,text='Title',size=24.0,font='Arial')

    def test_selected_named_style_overrides_model_weight(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);path=root/'layout.json'
            path.write_text(json.dumps({'width':600,'height':1200,'background':'#ffffff','elements':[{'kind':'text','x':20,'y':80,'text':'Title','size':48,'font':'Arial','fontStyle':'Bold Italic','weight':400}]}))
            bridge=Mock();bridge.exchange=root
            build_layout(bridge,path,root)
            bridge.client.run.assert_any_call('type.create',x=20,y=80,text='Title',size=48.0,font='Arial',fontStyle='Bold Italic')

    def test_history_distinguishes_target_sizes_and_restores_settings(self):
        from photocraft_ai.history import History
        with tempfile.TemporaryDirectory() as directory:
            history=History(directory)
            request={'mode':'layout','prompt':'base','layout_options':{'reference_size':False,'width':600,'height':1200,'dpi':300,'font':'Arial'}}
            first=history.save(request)
            self.assertEqual(first,history.save(request))
            self.assertEqual(history.restore(first)['layout_options']['height'],1200)
            request['layout_options']['height']=600
            self.assertNotEqual(first,history.save(request))
    def test_only_declarative_editable_elements_are_allowed(self):
        value={'width':640,'height':480,'background':'#ffffff','elements':[{'kind':'text','x':10,'y':30,'text':'Title','size':24}]}
        self.assertEqual(validate_layout(value),value)
        for change in [{'elements':[{'kind':'image','x':0,'y':0,'path':'secret'}]}, {'width':100000}, {'background':'url(file://private)'}, {'elements':[{'kind':'text','x':float('nan'),'y':0,'text':'x'}]}]:
            with self.assertRaises(ValueError):validate_layout({**value,**change})

    def test_anchor_copy_selects_original_layer_instead_of_top(self):
        bridge=object.__new__(PhotoCraftBridge);bridge.client=Mock();bridge.activate=Mock();bridge._copy_in=Mock(return_value=99);bridge._result_anchor=7
        self.assertEqual(bridge._copy_on_top(object(),1,2),99)
        bridge.client.run.assert_called_once_with('layer.select',layer=7)

    def test_no_selection_keeps_top_fallback(self):
        bridge=object.__new__(PhotoCraftBridge);bridge.client=Mock();bridge.activate=Mock();bridge._copy_in=Mock(return_value=99);bridge._top_layer=Mock(return_value=10);bridge._result_anchor=None
        self.assertEqual(bridge._copy_on_top(object(),1,2),99)
        bridge.client.run.assert_called_once_with('layer.select',layer=10)

    def test_bounded_bezier_paths_and_font_weights(self):
        value={'width':640,'height':480,'background':'#ffffff','elements':[{'kind':'path','x':0,'y':0,'fill':None,'stroke':'#00aaff','points':[{'anchor':[10,10],'in':[10,10],'out':[20,30]},[40,60]]}]}
        self.assertEqual(validate_layout(value),value)
        value['elements'][0]['points']=[{'anchor':[1,2],'command':'execute'},[4,5]]
        with self.assertRaises(ValueError):validate_layout(value)
