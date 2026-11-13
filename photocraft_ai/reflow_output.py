"""Publish a completed reflow beside its saved source without overwriting files."""
from pathlib import Path
import shutil


def copy_beside(staging,source,width,height,*,pending=False):
    source=Path(source)
    if not source.is_absolute():raise ValueError('Project path must be absolute')
    parent=source.parent.resolve(strict=True)
    base=f'{source.stem}_自适应_{width}x{height}'
    if pending:base+='_待审查'
    for index in range(1,10001):
        output=parent/(base+('' if index==1 else f'_{index}')+'.psd')
        try:handle=output.open('xb')
        except FileExistsError:continue
        try:
            with handle,Path(staging).open('rb') as data:shutil.copyfileobj(data,handle)
        except BaseException:
            output.unlink(missing_ok=True)
            raise
        return output
    raise ValueError('Too many existing PSD adaptations')
