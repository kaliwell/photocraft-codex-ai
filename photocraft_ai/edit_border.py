"""Constrain explicit side-border outpainting to confidently detected white margins."""
import re
import numpy as np
from PIL import Image,ImageChops


def refine_border_mask(full,mask,prompt):
    # Ordinary fills keep the user's exact mask. Only a specific request to fill
    # white side margins permits this narrower, content-preserving edit region.
    if not (re.search(r'白(?:色)?\s*(?:边框|边|留白)|white\s+(?:side\s+)?(?:borders?|margins?)',prompt,re.I)
            and re.search(r'左右|两侧|两边|left.*right|side',prompt,re.I)
            and re.search(r'移除|去掉|去除|补全|填充|扩图|remove|fill|extend|outpaint',prompt,re.I)):
        return mask,None
    bounds=mask.getbbox()
    if not bounds or bounds[0]!=0 or bounds[2]!=full.width:return mask,None
    pixels=np.asarray(full.convert('RGBA').crop((0,bounds[1],full.width,bounds[3])))
    rgb=pixels[:,:,:3]
    white=(rgb.min(axis=2)>=248)&((rgb.max(axis=2)-rgb.min(axis=2))<=3)&(pixels[:,:,3]>=254)
    columns=np.mean(white,axis=0)>=.995
    content=np.flatnonzero(~columns)
    if not content.size:return mask,None
    left=int(content[0]);right=full.width-int(content[-1])-1
    minimum=max(4,full.width//500)
    if min(left,right)<minimum or max(left,right)>full.width*.35:return mask,None
    seam=max(2,min(16,round(full.width*.004)))
    support=Image.new('L',full.size)
    support.paste(255,(0,0,left+seam,full.height))
    support.paste(255,(full.width-right-seam,0,full.width,full.height))
    refined=ImageChops.multiply(mask.convert('L'),support)
    return refined,{'method':'white-side-borders','left':left,'right':right,'seam':seam,'original_bounds':list(bounds)}


BORDER_INSTRUCTION='\nExtend the scene ONLY into the marked white side margins and their narrow joining seams. The central photo, product, certificate, text, window and all unmarked pixels must remain at their exact original positions and scale. Do not reframe, crop, zoom, remove physical frames, or redesign the central image.'


def alignment_mask(mask,border):
    """Blank margins are not registration landmarks, even beyond the edit mask.

    This exclusion is only for estimating alignment. The original narrowed mask
    still controls every output pixel, including its unselected rows and holes.
    """
    if (border.get('method')!='white-side-borders'
            or any(type(border.get(k)) is not int for k in ('left','right','seam'))
            or not 0<min(border['left'],border['right'])<=max(border['left'],border['right'])<=mask.width*.35
            or not 0<=border['seam']<=16):
        raise ValueError('Invalid side-border alignment metadata')
    exclusion=Image.new('L',mask.size)
    exclusion.paste(255,(0,0,border['left']+border['seam'],mask.height))
    exclusion.paste(255,(mask.width-border['right']-border['seam'],0,mask.width,mask.height))
    return ImageChops.lighter(mask.convert('L'),exclusion)
