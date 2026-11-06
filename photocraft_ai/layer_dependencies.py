"""Groups whose clipping or masks require a shared transform."""


def protected_group(row):
    return bool(row.get('children')) and (row.get('hasMask',False) or row.get('hasVectorMask',False) or any(child.get('clipped',False) for child in row['children']))
