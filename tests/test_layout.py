import unittest
from unittest.mock import Mock
from photocraft_ai.layout import validate_layout
from photocraft_ai.bridge import PhotoCraftBridge


class LayoutTests(unittest.TestCase):
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
