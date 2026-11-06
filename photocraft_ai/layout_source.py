"""Read selected layers through an isolated transparent scratch document."""
import base64
import uuid


def selected_layer_reference(bridge):
    image=bridge.active_image()
    if image is None:raise ValueError('Select source layers first')
    bridge.activate(image)
    info=bridge.client.run('document.inspect')
    layers=info.get('selectedLayers',[])
    if not layers:raise ValueError('Select source layers first')
    if info['width']*info['height']>32_000_000:raise ValueError('PSD exceeds 32 million pixels')
    scratch=None
    path=bridge.exchange/f'selected-layout-source-{uuid.uuid4().hex}.png'
    try:
        bridge.client.run('file.new',width=info['width'],height=info['height'],background='transparent')
        scratch=bridge.client.run('session.inspect')['active']
        bridge.client.run('layer.copyToDocument',source=image.index,document=scratch,layers=layers)
        bridge.client.call('app.save',path=str(path))
        data=path.read_bytes()
    finally:
        try:
            if scratch is not None:
                bridge.client.run('document.activate',document=scratch)
                bridge.client.run('file.close')
        finally:
            bridge.activate(image)
            path.unlink(missing_ok=True)
    return [{'name':'Selected layers.png','data':base64.b64encode(data).decode('ascii')}]
