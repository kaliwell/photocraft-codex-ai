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
