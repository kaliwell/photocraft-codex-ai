"""Visible clipping bounds and independent clusters inside mixed folders."""


def union(boxes):
    boxes=[b for b in boxes if b and b[2]>0 and b[3]>0]
    if not boxes:return None
    x=min(b[0] for b in boxes);y=min(b[1] for b in boxes)
    return [x,y,max(b[0]+b[2] for b in boxes)-x,max(b[1]+b[3] for b in boxes)-y]


def intersect(a,b):
    if not a or not b:return None
    x=max(a[0],b[0]);y=max(a[1],b[1]);right=min(a[0]+a[2],b[0]+b[2]);bottom=min(a[1]+a[3],b[1]+b[3])
    return [x,y,max(0,right-x),max(0,bottom-y)]


def child_boxes(rows):
    result=[None]*len(rows);base=None
    for i in range(len(rows)-1,-1,-1):
        row=rows[i];box=visible_bounds(row) if row.get('visible',True) else None
        if row.get('clipped'):box=intersect(box,base)
        else:base=box
        result[i]=box
    return result


def visible_bounds(row):
    return union(child_boxes(row['children'])) if row.get('children') else row.get('bounds')


def mixed_clusters(row):
    rows=row.get('children',[]);boxes=child_boxes(rows)
    bases=[i for i,r in enumerate(rows) if not r.get('clipped') and i>0 and rows[i-1].get('clipped') and boxes[i]]
    if len(bases)>1:
        return panel_clusters(row,boxes,bases)
    if len(bases)!=1 or row.get('hasMask') or row.get('hasVectorMask') or row.get('effects',{}).get('enabled') or any(r['kind'] in ('Adjustment','Fill') for r in rows):return None
    base=bases[0];b=boxes[base];inside=[];outside=[]
    if rows[base]['kind']!='Shape':return None
    for i,box in enumerate(boxes):
        if not box or box[2]<=0 or box[3]<=0:continue
        cx,cy=box[0]+box[2]/2,box[1]+box[3]/2
        (inside if b[0]-20<=cx<=b[0]+b[2]+20 and b[1]-20<=cy<=b[1]+b[3]+20 else outside).append(i)
    if not outside:return None
    if not any(rows[i]['kind']=='Type' for i in outside):return None
    # Separate only clearly unrelated material, far from the clipping panel.
    merged=union([boxes[i] for i in inside+outside])
    if merged[2]*merged[3]<b[2]*b[3]*2:return None
    groups=[inside] if inside else []
    def near(i,j):
        b=boxes[j];overlap=intersect([b[0]-40,b[1]-40,b[2]+80,b[3]+80],boxes[i])
        return overlap and overlap[2]>0 and overlap[3]>0
    while outside:
        group=[outside.pop(0)];changed=True
        while changed:
            changed=False
            for i in outside[:]:
                if any(near(i,j) for j in group):
                    group.append(i);outside.remove(i);changed=True
        text=[i for i in group if rows[i]['kind']=='Type']
        if len(text)>1:
            groups.extend([[i] for i in text])
            other=[i for i in group if i not in text]
            if other:groups.append(other)
        else:groups.append(group)
    return [(indices,union([boxes[i] for i in indices])) for indices in groups]


def panel_clusters(row,boxes,clipped_bases):
    rows=row['children']
    if row.get('hasMask') or row.get('hasVectorMask') or row.get('clipped') or row.get('effects',{}).get('enabled') or row.get('opacity',1)!=1 or row.get('fill',1)!=1:return None
    if row.get('blend','Normal') not in ('Normal','Pass Through'):return None
    if any(r['kind'] in ('Adjustment','Fill') for r in rows):return None
    bases=[i for i,r in enumerate(rows) if r['kind']=='Shape' and not r.get('clipped') and boxes[i]]
    if any(i not in bases for i in clipped_bases):return None
    for n,i in enumerate(bases):
        for j in bases[n+1:]:
            overlap=intersect(boxes[i],boxes[j])
            if overlap and overlap[2]*overlap[3]>min(boxes[i][2]*boxes[i][3],boxes[j][2]*boxes[j][3])*.01:return None
    groups={i:[i] for i in bases};used=set(bases)
    for i in bases:
        j=i-1
        while j>=0 and rows[j].get('clipped'):
            groups[i].append(j);used.add(j);j-=1
    for i,box in enumerate(boxes):
        if i in used or not box or box[2]<=0 or box[3]<=0:continue
        if rows[i].get('clipped'):return None
        cx,cy=box[0]+box[2]/2,box[1]+box[3]/2
        candidates=[b for b in bases if boxes[b][0]<=cx<=boxes[b][0]+boxes[b][2] and boxes[b][1]<=cy<=boxes[b][1]+boxes[b][3]]
        if len(candidates)!=1:return None
        groups[candidates[0]].append(i)
    return [(sorted(indices),union([boxes[i] for i in indices])) for indices in groups.values()]


def bind_panel_labels(units,at):
    """A caption in a different folder still follows the card underneath it."""
    panels=[]
    for unit in units:
        paths=unit.get('paths',[])
        shapes=[at(p) for p in paths if at(p)['kind']=='Shape']
        if len(shapes)==1 and shapes[0].get('bounds'):
            unit['peer_panel']=shapes[0]['bounds'][2:];panels.append(unit)
    removed=[]
    for unit in units:
        if unit['kind']!='Type' or unit.get('paths'):continue
        box=unit['bounds'];area=box[2]*box[3]
        matches=[]
        for panel in panels:
            overlap=intersect(box,panel['bounds'])
            if overlap and overlap[2]*overlap[3]>=area*.8:matches.append(panel)
        if len(matches)==1:
            matches[0]['paths'].append(unit['path']);matches[0]['name']+=' / '+unit['name'];removed.append(unit)
    return [u for u in units if u not in removed]


def bind_product_callouts(units,at):
    """Keep a narrow product and its neighbouring arrow/text block in one frame."""
    def descendants(row):return [row]+[r for child in row.get('children',[]) for r in descendants(child)]
    removed=[]
    for product in units:
        box=product['bounds'];rows=descendants(at(product['path']))
        if product.get('paths') or box[3]<box[2]*4 or not any(r['kind']=='Smart Object' and r.get('visible',True) for r in rows):continue
        choices=[]
        for labels in units:
            if labels is product or labels in removed or labels.get('paths') or labels['kind']!='Group':continue
            parts=descendants(at(labels['path']));texts=sum(r['kind']=='Type' and r.get('visible',True) for r in parts)
            arrows=[r for r in parts if r['kind']=='Pixel' and r.get('bounds') and r['bounds'][2]>r['bounds'][3]*2]
            other=labels['bounds'];overlap=max(0,min(box[1]+box[3],other[1]+other[3])-max(box[1],other[1]))
            gap=other[0]-(box[0]+box[2])
            if texts>=2 and len(arrows)>=2 and -20<=gap<=80 and overlap>=min(box[3],other[3])*.75:choices.append(labels)
        if len(choices)!=1:continue
        labels=choices[0];product['paths']=[product['path'],labels['path']];product['bounds']=union([box,labels['bounds']]);product['name']+=' / '+labels['name'];removed.append(labels)
        # A masked motion-blurred shadow is a support layer of this product. Its
        # oversized filter bounds must not define the product's layout rectangle.
        for shadow in units:
            if shadow in removed:continue
            r=at(shadow['path']);b=shadow['bounds']
            if shadow.get('paths') or not r.get('hasMask') or r['kind']!='Smart Object':continue
            if not any(f.get('command')=='filter.blur.motionBlur' for f in r.get('smartFilters',[])):continue
            if b[3]<box[3]*.15 and abs(b[1]-(box[1]+box[3]))<box[3]*.15 and abs(b[0]-box[0])<max(80,box[2]):
                product['paths'].append(shadow['path']);removed.append(shadow)
                product.setdefault('rasterize_support_paths',[]).append(shadow['path'])
    return [u for u in units if u not in removed]
