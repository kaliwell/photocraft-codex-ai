"""PhotoCraft transport, adapted from OpenFill (Apache-2.0)."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'vendor'))
from openfill_photocraft.bridge import PhotoCraftBridge as _Bridge, BridgeError
from openfill_photocraft.control import ControlClient, ControlError
from openfill.geometry import Rect


class PhotoCraftBridge(_Bridge):
    """Keep AI mask feather as an editable native mask property."""
    def _mask_image(self, image, layer, size):
        if layer.mask_kind != 'pixels':
            return super()._mask_image(image, layer, size)
        feather = layer.feather
        try:
            layer.feather = 0
            return super()._mask_image(image, layer, size)
        finally:
            layer.feather = feather

    def _add_mask(self, scratch, layer_id, kind, grow, feather, mask_doc, mask_layer):
        super()._add_mask(scratch, layer_id, kind, grow, 0 if kind == 'pixels' else feather, mask_doc, mask_layer)
        if kind == 'pixels' and feather:
            self.client.run('layer.layerMask.edit', layer=layer_id, feather=feather)

__all__ = ['PhotoCraftBridge', 'BridgeError', 'ControlClient', 'ControlError', 'Rect']
