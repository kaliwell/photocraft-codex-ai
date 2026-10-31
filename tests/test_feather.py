import unittest
from PIL import Image, ImageChops, ImageDraw

from photocraft_ai.service import inward_feather, clipped_layer


class FeatherTests(unittest.TestCase):
    def rectangle(self):
        mask = Image.new('L', (100, 100), 0)
        ImageDraw.Draw(mask).rectangle((10, 10, 89, 89), fill=255)
        return mask

    def test_edge_fades_in_while_interior_is_opaque(self):
        feather = inward_feather(self.rectangle(), 12)
        values = [feather.getpixel((x, 50)) for x in (9, 10, 12, 16, 21, 50)]
        self.assertEqual(values[0], 0)
        self.assertGreater(values[1], 0)
        self.assertLess(values[1], values[2])
        self.assertEqual(values, sorted(values))
        self.assertEqual(values[-1], 255)

    def test_composite_never_changes_outside_selection(self):
        mask = self.rectangle()
        base = Image.new('RGBA', mask.size, 'blue')
        layer = clipped_layer(Image.new('RGBA', mask.size, 'red'), mask, 12)
        result = Image.alpha_composite(base, layer)
        difference = ImageChops.difference(base.convert('RGB'), result.convert('RGB'))
        outside = ImageChops.invert(mask)
        self.assertTrue(all(ImageChops.multiply(c, outside).getbbox() is None for c in difference.split()))
        self.assertEqual(result.getpixel((50, 50)), (255, 0, 0, 255))
        edge = result.getpixel((10, 50))
        self.assertTrue(0 < edge[0] < 255 and 0 < edge[2] < 255)

    def test_holes_and_irregular_selection_stay_clear(self):
        mask = self.rectangle()
        ImageDraw.Draw(mask).ellipse((35, 35, 65, 65), fill=0)
        feather = inward_feather(mask, 12)
        self.assertEqual(feather.getpixel((50, 50)), 0)
        self.assertTrue(all(a <= b for a, b in zip(feather.getdata(), mask.getdata())))

    def test_existing_soft_coverage_is_not_increased(self):
        mask = Image.new('L', (50, 50), 128)
        feather = inward_feather(mask, 8)
        self.assertEqual(feather.getpixel((25, 25)), 128)
        self.assertTrue(0 < feather.getpixel((0, 25)) < 128)

    def test_one_pixel_selection_survives(self):
        mask = Image.new('L', (20, 20), 0)
        mask.putpixel((10, 10), 255)
        self.assertEqual(inward_feather(mask, 12).getpixel((10, 10)), 255)

    def test_zero_radius_retains_exact_original_mask(self):
        mask = self.rectangle()
        self.assertEqual(inward_feather(mask, 0).tobytes(), mask.tobytes())


if __name__ == '__main__':
    unittest.main()
