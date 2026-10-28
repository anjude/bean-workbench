#!/usr/bin/env python3
"""独立枚举并用无猜测规则推导鹅在哪里关卡。"""
import itertools
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[5]
source = root / 'business-repo/uni-gknow/src/data/gooseGridLevels.ts'
levels = re.findall(r'regions:\s*(\[\[.*?\]\]),\s*solution:\s*(\[.*?\])', source.read_text())
assert len(levels) == 5, '应有五关'


def verify(regions, answer):
    n = len(answer)
    assert len(regions) == n and all(len(row) == n for row in regions)
    assert sorted(set(sum(regions, []))) == list(range(n))
    groups = []
    for r in range(n):
        groups.append((f'第{r+1}行', {r*n+c for c in range(n)}))
    for c in range(n):
        groups.append((f'第{c+1}列', {r*n+c for r in range(n)}))
    for color in range(n):
        cells = {r*n+c for r in range(n) for c in range(n) if regions[r][c] == color}
        visited = {min(cells)}
        while True:
            neighbours = set(visited)
            for index in visited:
                r,c = divmod(index,n)
                for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
                    rr,cc = r+dr,c+dc
                    if 0 <= rr < n and 0 <= cc < n and rr*n+cc in cells:
                        neighbours.add(rr*n+cc)
            if neighbours == visited:
                break
            visited = neighbours
        assert visited == cells, f'颜色区域 {color} 不连续'
        groups.append((f'颜色{color}', cells))
    valid = [p for p in itertools.permutations(range(n))
             if all(abs(p[r]-p[r+1]) > 1 for r in range(n-1))
             and len({regions[r][p[r]] for r in range(n)}) == n]
    assert len(valid) == 1 and list(valid[0]) == answer, f'答案不唯一或不匹配: {valid}'

    # 根据已确定的鹅排除同行、同列、同色和周围八格；
    # 某区域/行/列的所有候选落入另一行、列或区域时，另一组其余格可排除。
    candidates = set(range(n*n))
    placed = set()
    trace = []
    while len(placed) < n:
        progress = False
        for name, group in groups:
            if group & placed:
                continue
            options = group & candidates
            assert options, f'{name} 没有候选'
            if len(options) == 1:
                index = next(iter(options)); r,c = divmod(index,n)
                placed.add(index)
                forbidden = set().union(*(other for _,other in groups if index in other))
                forbidden |= {rr*n+cc for rr in range(max(0,r-1),min(n,r+2))
                              for cc in range(max(0,c-1),min(n,c+2))}
                candidates -= forbidden
                trace.append(f'{name}只剩第{r+1}行第{c+1}列')
                progress = True
                break
        if progress:
            continue
        for a_name,a in groups:
            if a & placed:
                continue
            options = a & candidates
            if len(options) < 2:
                continue
            for b_name,b in groups:
                if a is b or b & placed or not options <= b:
                    continue
                removed = (b-a) & candidates
                if removed:
                    candidates -= removed
                    trace.append(f'{a_name}的候选都在{b_name}，排除该组其他{len(removed)}格')
                    progress = True
                    break
            if progress:
                break
        assert progress, f'仅凭基础排除无法继续，已找到 {len(placed)} 只鹅'
    assert {r*n+c for r,c in enumerate(answer)} == placed
    return trace

for index, (region_json, answer_json) in enumerate(levels, 1):
    regions, answer = json.loads(region_json), json.loads(answer_json)
    steps = verify(regions, answer)
    print(f'第 {index} 关：唯一解，逐步排除 {len(steps)} 步')
    for step in steps:
        print('  ' + step)
