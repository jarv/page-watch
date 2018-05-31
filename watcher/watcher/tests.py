from django.test import TestCase
from path import path
from watcher.util import make_sure_path_exists
from watcher.image import create_thumbnail, crop_to_max, crop_to_match
import tempfile
from PIL import Image
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ImageTestCase(TestCase):

    def setUp(self):
        self.temp_dir = path(tempfile.mkdtemp())
        make_sure_path_exists(self.temp_dir)

    def tearDown(self):
        self.temp_dir.rmtree()

    def test_thumbnail(self):
        capture = self.temp_dir / 'capture-test.png'
        size = (800, 1024)
        im = Image.new('RGB', size)
        im.save(capture)
        thumb = create_thumbnail(capture)

        self.assertTrue(thumb.exists())
        with Image.open(thumb) as im:
            (w, h) = im.size
            self.assertLessEqual(w, settings.SMALL_WIDTH)
            self.assertLessEqual(h, settings.SMALL_HEIGHT)

    def test_crop_to_max(self):
        capture = self.temp_dir / 'capture-test.png'
        size = (8000, 10000)
        im = Image.new('RGB', size)
        im.save(capture)
        capture = crop_to_max(capture)
        self.assertTrue(capture.exists())
        with Image.open(capture) as im:
            (w, h) = im.size
            self.assertLessEqual(w, settings.MAX_WIDTH)
            self.assertLessEqual(h, settings.MAX_HEIGHT)

    def test_crop_to_match(self):
        sizes = [
            ((200, 200), (200, 200)),
            ((200, 200), (500, 500)),
            ((500, 500), (200, 200)),
            ((500, 200), (200, 200)),
            ((200, 500), (200, 200)),
            ((200, 200), (500, 200)),
            ((200, 200), (200, 500)),
        ]
        for index, size in enumerate(sizes):
            cur = self.temp_dir / "cur-{}.png".format(index)
            resize_cur = self.temp_dir / settings.RESIZED_PREFIX + "cur-{}.png".format(index)
            last = self.temp_dir / "last-{}.png".format(index)
            resize_last = self.temp_dir / settings.RESIZED_PREFIX + "last-{}.png".format(index)
            im = Image.new('RGB', size[0])
            im.save(cur)
            im_l = Image.new('RGB', size[1])
            im_l.save(last)
            crop_to_match(cur, last)
            with Image.open(resize_cur) as im, Image.open(resize_last) as l_im:
                w, h = im.size
                l_w, l_h = l_im.size
                self.assertEqual(w, l_w)
                self.assertEqual(h, l_h)
