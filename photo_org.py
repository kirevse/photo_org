import datetime
import os
import sys
import shutil
import PIL.ExifTags
import PIL.Image


def get_exif(filename):
    with PIL.Image.open(filename) as image:
        image.verify()
        return {PIL.ExifTags.TAGS.get(key): value for (key, value) in image._getexif().items()}


if __name__ == '__main__':
    if len(sys.argv) < 2:
        exit(-1)

    srcdir = sys.argv[1]
    dstdir = sys.argv[2]
    for (dirname, subdirs, filenames) in os.walk(srcdir):
        for filename in filenames:
            if filename[-4:].lower().endswith('.jpg'):
                srcfilepath = '{}\{}'.format(dirname, filename)
                exif = get_exif('{}\{}'.format(dirname, filename))
                cameradir = '{} {}'.format(exif['Make'], exif['Model'])
                original_dt = datetime.datetime.strptime(
                    exif['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
                dstdirpath = '{}\{}\{}\{}\{}'.format(dstdir, cameradir, original_dt.year, original_dt.strftime(
                    '%Y-%m'), original_dt.strftime('%Y-%m-%d'))
                os.makedirs(dstdirpath, exist_ok=True)
                dstfilepath = '{}\{}'.format(dstdirpath, filename)
                print('{} => {}'.format(srcfilepath, dstfilepath))
                shutil.copy(srcfilepath, dstfilepath)
