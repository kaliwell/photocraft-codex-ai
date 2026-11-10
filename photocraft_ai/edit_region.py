"""Selection-local image references and a single-pass return coordinate mapping."""
import math
from PIL import Image,ImageOps


def prepare_region(full,mask):
    if full.size!=mask.size:raise ValueError('Selection and canvas dimensions differ')
    bounds=mask.getbbox()
    if bounds is None:raise ValueError('Empty edit selection')
    x0,y0,x1,y1=bounds
    margin=max(64,round(max(x1-x0,y1-y0)*.20))
    crop=(max(0,x0-margin),max(0,y0-margin),min(full.width,x1+margin),min(full.height,y1+margin))
    content=full.crop(crop).convert('RGBA')
    fitted=ImageOps.contain(content,(1536,1536),Image.Resampling.LANCZOS) if max(content.size)>1536 else content
    side=max(256,math.ceil(max(fitted.size)/16)*16)
    x,y=(side-fitted.width)//2,(side-fitted.height)//2
    source=Image.new('RGBA',(side,side));source.paste(fitted,(x,y))
    selected=mask.crop(crop).resize(fitted.size,Image.Resampling.LANCZOS)
    selection=Image.new('L',source.size);selection.paste(selected,(x,y))
    mapping={'version':2,'canvas_size':list(full.size),'crop_box':list(crop),'source_size':[side,side],'content_box':[x,y,x+fitted.width,y+fitted.height]}
    return source,selection,mapping


def map_result(image,mask,mapping):
    source_size=mapping.get('source_size',[1024,1024])
    crop=mapping.get('crop_box',[0,0,*mask.size])
    box=mapping['content_box']
    def rect(value,limits):
        return isinstance(value,(list,tuple)) and len(value)==4 and all(type(n) is int for n in value) and 0<=value[0]<value[2]<=limits[0] and 0<=value[1]<value[3]<=limits[1]
    if not isinstance(source_size,(list,tuple)) or len(source_size)!=2 or any(type(n) is not int or not 1<=n<=1536 for n in source_size):raise ValueError('Invalid edit reference size')
    if mapping.get('canvas_size',list(mask.size))!=list(mask.size) or not rect(crop,mask.size) or not rect(box,source_size):raise ValueError('Invalid edit coordinate mapping')
    bounds=mask.getbbox()
    if bounds and not (crop[0]<=bounds[0] and crop[1]<=bounds[1] and crop[2]>=bounds[2] and crop[3]>=bounds[3]):raise ValueError('Edit crop omits selected pixels')
    # Map to raw returned pixels, rather than shrinking the result to input size.
    raw=(box[0]*image.width/source_size[0],box[1]*image.height/source_size[1],box[2]*image.width/source_size[0],box[3]*image.height/source_size[1])
    region=image.convert('RGBA').resize((crop[2]-crop[0],crop[3]-crop[1]),Image.Resampling.LANCZOS,box=raw)
    layer=Image.new('RGBA',mask.size);layer.paste(region,crop[:2])
    return layer
