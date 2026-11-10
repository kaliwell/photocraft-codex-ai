"""Estimate bounded registration using only unchanged selection context."""
import cv2
import numpy as np
from PIL import Image


class AlignmentError(RuntimeError):
    pass


def estimate(original,candidate,mask):
    scale=min(1,768/max(original.size));size=tuple(max(1,round(n*scale)) for n in original.size)
    a=cv2.cvtColor(np.array(original.convert('RGB').resize(size,Image.Resampling.LANCZOS)),cv2.COLOR_RGB2GRAY)
    b=cv2.cvtColor(np.array(candidate.convert('RGB').resize(size,Image.Resampling.LANCZOS)),cv2.COLOR_RGB2GRAY)
    valid=(np.array(mask.resize(size,Image.Resampling.NEAREST))==0).astype('uint8')*255
    valid=cv2.erode(valid,np.ones((9,9),np.uint8));valid[:4]=0;valid[-4:]=0;valid[:,:4]=0;valid[:,-4:]=0
    identity=np.eye(2,3,dtype=np.float32)
    selected=valid>0
    if np.count_nonzero(selected)<256:return identity,{'status':'no_context','matrix':identity.tolist()}
    initial=float(np.mean(np.abs(a[selected].astype(float)-b[selected])))
    if initial<.01:return identity,{'status':'context_matches','context_error':initial,'matrix':identity.tolist()}
    if float(np.std(a[selected]))<3:
        if initial>8:raise AlignmentError('返回图片与原图边界不一致，结果已保留，未导入。请缩小选区后重试。')
        return identity,{'status':'flat_context','context_error':initial,'matrix':identity.tolist()}
    try:
        score,warp=cv2.findTransformECC(a,b,identity.copy(),cv2.MOTION_AFFINE,(cv2.TERM_CRITERIA_COUNT|cv2.TERM_CRITERIA_EPS,150,1e-6),inputMask=valid,gaussFiltSize=5)
    except cv2.error as error:
        raise AlignmentError('无法可靠对齐返回图片，结果已保留，未导入。请缩小选区后重试。') from error
    native=warp.copy();native[:,2]/=scale
    linear=native[:,:2];singular=np.linalg.svd(linear,compute_uv=False)
    corners=np.float32([[0,0,1],[original.width,0,1],[0,original.height,1],[original.width,original.height,1]])
    displacement=float(np.max(np.linalg.norm(corners@native.T-corners[:,:2],axis=1)))
    if not np.isfinite(native).all() or not np.isfinite(score) or score<.95 or np.linalg.det(linear)<=0 or min(singular)<.94 or max(singular)>1.06 or displacement>max(8,min(64,max(original.size)*.08)):
        raise AlignmentError('返回图片构图偏移过大，结果已保留，未导入。请缩小选区后重试。')
    aligned=cv2.warpAffine(b,warp,size,flags=cv2.INTER_LINEAR|cv2.WARP_INVERSE_MAP,borderMode=cv2.BORDER_REPLICATE)
    error=float(np.mean(np.abs(a[selected].astype(float)-aligned[selected])))
    # Validate spatially separate context areas, not just a global average.
    for y0,y1 in ((0,size[1]//2),(size[1]//2,size[1])):
        for x0,x1 in ((0,size[0]//2),(size[0]//2,size[0])):
            keep=selected[y0:y1,x0:x1];aa=a[y0:y1,x0:x1][keep];bb=aligned[y0:y1,x0:x1][keep]
            if aa.size>=128 and np.std(aa)>5 and np.corrcoef(aa,bb)[0,1]<.90:
                raise AlignmentError('返回图片局部边界无法接齐，结果已保留，未导入。请缩小选区后重试。')
    if error>max(8,initial) or error>16:raise AlignmentError('返回图片边界变化过大，结果已保留，未导入。')
    return native,{'status':'aligned','score':float(score),'before_error':initial,'after_error':error,'max_displacement':displacement,'matrix':native.tolist()}


def render(raw,mapping,size,matrix):
    sw,sh=mapping['source_size'];left,top,right,bottom=mapping['content_box']
    sx=(right-left)*raw.width/sw/size[0];sy=(bottom-top)*raw.height/sh/size[1]
    combined=np.array(matrix,dtype=np.float64).copy()
    combined[0]*=sx;combined[1]*=sy
    combined[0,2]+=left*raw.width/sw;combined[1,2]+=top*raw.height/sh
    # Registration and coordinate mapping share one sampling pass from raw pixels.
    pixels=cv2.warpAffine(np.array(raw.convert('RGBA')),combined,size,flags=cv2.INTER_LANCZOS4|cv2.WARP_INVERSE_MAP,borderMode=cv2.BORDER_CONSTANT)
    return Image.fromarray(pixels)
