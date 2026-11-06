"""Independent PSD conversion with durable per-item results and cancellation."""
import json
import re
from pathlib import Path
from types import SimpleNamespace
from PIL import Image
from .backend import Cancelled
from .layout import generate_layout, build_layout


def run_batch(service, prepared, cancel, progress):
    output=service.bridge.exchange/('batch-'+prepared.job.name)
    output.mkdir(exist_ok=False)
    names=json.loads((prepared.job/'job.json').read_text(encoding='utf8'))['references']
    report={'output':str(output),'items':[{'source':name,'status':'pending'} for name in names]}
    def save():
        for folder in (prepared.job,output):
            temporary=folder/'batch-report.tmp'
            temporary.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
            temporary.replace(folder/'batch-report.json')
    save()
    for index,reference in enumerate(prepared.references):
        item=report['items'][index]
        if cancel.is_set():save();raise Cancelled('Cancelled')
        stem=re.sub(r'[^\w .-]','_',Path(item['source']).stem,flags=re.UNICODE).strip(' .')[:60] or 'reference'
        job=prepared.job/f'{index+1:03}_{stem}';job.mkdir()
        item['status']='running';save()
        message=f'Batch PSD {index+1}/{len(prepared.references)}: {item["source"]}'
        progress(message)
        try:
            with Image.open(reference) as image:long_page=image.height>8192
            layout=generate_layout(job,[reference],prepared.prompt,cancel,lambda _:progress(message),prepared.layout_options,long_page=long_page)
            if cancel.is_set():raise Cancelled('Cancelled')
            with service.lock:
                bridge=SimpleNamespace(client=service.bridge.client,exchange=output)
                path=build_layout(bridge,layout,job)
            item.update(status='success',psd=str(path))
        except Cancelled:
            item['status']='cancelled';save();raise
        except Exception as error:
            item.update(status='failed',error=str(error))
        save()
    return report
