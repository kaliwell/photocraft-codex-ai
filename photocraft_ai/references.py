"""Bounded, explicit reference-image attachments; never accept filesystem paths over HTTP."""
import base64
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageOps

MAX_BYTES=64*1024*1024
MAX_TOTAL=256*1024*1024
MAX_PIXELS=100_000_000


def validate_references(items):
    if not isinstance(items,list):
        raise ValueError('参考图片参数必须为列表。')
    total=0
    for item in items:
        if not isinstance(item,dict) or set(item)!={'name','data'}:
            raise ValueError('参考图参数无效。')
        if not isinstance(item['name'],str) or not 1<=len(item['name'])<=255:
            raise ValueError('参考图名称无效。')
        data=item['data']
        if not isinstance(data,str) or len(data)>4*((MAX_BYTES+2)//3):
            raise ValueError('参考图超过本地传输保护阈值 64 MiB。')
        total+=(len(data)//4)*3-len(data)+len(data.rstrip('='))
    if total>MAX_TOTAL:
        raise ValueError('参考图超过本地传输保护阈值 256 MiB。')
    return items


def save_references(items,job:Path):
    validate_references(items)
    paths=[];names=[];total=0
    for index,item in enumerate(items,1):
        try:
            data=base64.b64decode(item['data'],validate=True)
        except (ValueError,TypeError) as error:
            raise ValueError('参考图编码无效。') from error
        total+=len(data)
        if not data or len(data)>MAX_BYTES or total>MAX_TOTAL:
            raise ValueError('参考图大小超出限制。')
        with Image.open(BytesIO(data)) as image:
            if image.width*image.height>MAX_PIXELS:
                raise ValueError('参考图超过本地解码保护阈值 1 亿像素。')
            image.load()
            upright=ImageOps.exif_transpose(image).convert('RGBA')
            fitted=upright
            fitted.info.clear()
            folder=job/'references';folder.mkdir(exist_ok=True)
            path=folder/f'reference-{index:02}.png';fitted.save(path)
            paths.append(path);names.append(item['name'])
    return tuple(paths),names
