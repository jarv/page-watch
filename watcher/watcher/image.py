from PIL import Image
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def crop_to_max(capture_file, url=None):
    if not url:
        url = "Unspecified"
    with Image.open(capture_file) as im:
        w, h = im.size
        if w > settings.MAX_WIDTH:
            logger.info("Cropping {} width {} > {} {}".format(url, w, settings.MAX_WIDTH, capture_file))
            im = im.crop((0, 0, settings.MAX_WIDTH, h))
            im.save(capture_file)
    with Image.open(capture_file) as im:
        w, h = im.size
        if h > settings.MAX_HEIGHT:
            logger.info("Cropping {} height {} > {} {}".format(url, h, settings.MAX_HEIGHT, capture_file))
            im = im.crop((0, 0, w, settings.MAX_HEIGHT))
            im.save(capture_file)
    return capture_file


def crop_to_match(img, l_img, url=None):
    """
    Given two images will crop one to match the
    other, this creates images with a resized
    prefix regardless of whether their size has
    changed for consistency and so that we don't
    lose the original
    """
    resized_img = img.dirname() / settings.RESIZED_PREFIX + img.basename()
    resized_l_img = l_img.dirname() / settings.RESIZED_PREFIX + l_img.basename()

    if not url:
        url = "Unspecified"
    with Image.open(img) as im, Image.open(l_img) as l_im:
        w, h = im.size
        l_w, l_h = l_im.size
        if w > l_w:
            logger.info("Cropping {} image width {} to match last image width {}".format(url, w, l_w))
            im = im.crop((0, 0, l_w, h))
        elif l_w > w:
            logger.info("Cropping {} last image width {} to match image width {}".format(url, l_w, w))
            l_im = l_im.crop((0, 0, w, l_h))
        l_im.save(resized_l_img)
        im.save(resized_img)
    with Image.open(resized_img) as im, Image.open(resized_l_img) as l_im:
        w, h = im.size
        l_w, l_h = l_im.size
        if h > l_h:
            logger.info("Cropping {} image height {} to match last image height {}".format(url, h, l_h))
            im = im.crop((0, 0, w, l_h))
        elif l_h > h:
            logger.info("Cropping {} last image height {} to match image height {}".format(url, l_h, h))
            l_im = l_im.crop((0, 0, l_w, h))
        l_im.save(resized_l_img)
        im.save(resized_img)


def create_thumbnail(capture_file):
    """
    Creates a thumbnail from a path to a capture file,
    returns the thumbnail filename
    """

    with Image.open(capture_file) as im:
        im.thumbnail((settings.SMALL_WIDTH, settings.SMALL_HEIGHT), Image.ANTIALIAS)
        fname = capture_file.dirname() / settings.SMALL_PREFIX + capture_file.basename()
        im.save(fname)
    return fname
