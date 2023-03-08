import collections
import datetime
import os
import re
import shutil
import sys
import PIL.ExifTags
import PIL.Image


def get_exif(filename):
    try:
        with PIL.Image.open(filename) as image:
            image.verify()
            return {PIL.ExifTags.TAGS.get(key): value for (key, value) in image._getexif().items()}
    except BaseException as exception:
        print('Failed to retrieve EXIF data: ', getattr(exception, 'message', str(exception)))   
        return None


def get_destdirpath(srcfilepath):
    exif = get_exif(srcfilepath)
    if exif is None:
        print('No EXIF found on file {}'.format(srcfilepath))
        return None

    make = exif.get('Make')
    if make is None:
        print('Make is not provided in EXIF of file {}'.format(
            srcfilepath))
        return None

    model = exif.get('Model')
    if model is None:
        print('Model is not provided in EXIF of file {}'.format(
            srcfilepath))
        return None

    cameradir = re.sub('[^A-Za-z0-9():\- ]+', '', '{} {}'.format(make.strip(), model.strip()))

    if 'DateTimeOriginal' not in exif:
        return None

    date_time_original = re.sub(
        '[^A-Za-z0-9: ]+', '', exif['DateTimeOriginal'])
    original_dt = datetime.datetime.strptime(
        date_time_original, '%Y:%m:%d %H:%M:%S') if date_time_original is not None else None

    year_month = original_dt.strftime('%Y-%m')
    year_month_day = original_dt.strftime('%Y-%m-%d')
    return f'{cameradir}/{original_dt.year}/{year_month}/{year_month_day}'
 

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'USAGE: {sys.argv[0]} <srcdir> <dstdir>')
        exit(-1)

    srcdir = sys.argv[1]
    dstdir = sys.argv[2]
    
    destdirpath_by_filekey = dict()
    srcfilepaths_by_filekey = dict()

    for (dirname, subdirs, filenames) in os.walk(srcdir):
        for filename in filenames:
            filekey = filename.upper().split('.')[0]
            srcfilepath = f'{dirname}\{filename}'
            if filename[-4:].lower().endswith('.jpg'):
                destdirpath = get_destdirpath(srcfilepath)
                if destdirpath is None:
                    continue
                destdirpath_by_filekey[filekey] = f'{dstdir}/{get_destdirpath(srcfilepath)}'
            srcfilepaths = srcfilepaths_by_filekey.get(filekey) or set()
            srcfilepaths_by_filekey[filekey] = srcfilepaths
            srcfilepaths.add(srcfilepath)

    for filekey, srcfilepaths in srcfilepaths_by_filekey.items():
        destdirpath = destdirpath_by_filekey.get(filekey)
        if destdirpath is None:
            continue
        if not os.path.exists(destdirpath):
            os.makedirs(destdirpath)
        for srcfilepath in srcfilepaths:
            print(f'{srcfilepath} => {destdirpath}')
            shutil.copy2(srcfilepath, destdirpath)
