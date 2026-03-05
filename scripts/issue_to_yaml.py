
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 Issue Form 的提交内容写入 products/<id>/product.yaml（如不存在则创建）
- 支持两条路径：新增产品、修改产品
- 依据标签 psms:add-product / psms:update-product 识别动作
- 不直接推主分支，由工作流后续步骤发起 PR
"""
import os, re, json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = ROOT / 'products'

ISSUE_BODY = os.environ.get('ISSUE_BODY', '')
ISSUE_LABELS = [l.get('name','') for l in json.loads(os.environ.get('ISSUE_LABELS','[]'))]

IS_ADD = 'psms:add-product' in ISSUE_LABELS
IS_UPDATE = 'psms:update-product' in ISSUE_LABELS

# ------- helpers -------

def _find_block_after(label: str):
    pattern = rf"###\s*{re.escape(label)}[^
]*
+([\s\S]*?)(?=
###|\Z)"
    m = re.search(pattern, ISSUE_BODY, re.IGNORECASE)
    return m.group(1).strip() if m else None

def _find_line_value(label_prefix: str):
    pattern = rf"###\s*{re.escape(label_prefix)}[^
]*
+([^
]+)"
    m = re.search(pattern, ISSUE_BODY, re.IGNORECASE)
    return m.group(1).strip() if m else None

def _parse_kv_lines(text: str):
    out = {}
    for ln in (text or '').splitlines():
        if '=' in ln:
            k, v = ln.split('=', 1)
            out[k.strip()] = v.strip()
    return out

def _load_yaml(p: Path):
    if p.exists():
        return yaml.safe_load(p.read_text(encoding='utf-8')) or {}
    return {}

def _dump_yaml(p: Path, data: dict):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding='utf-8')

# ------- main logic -------

def upsert_product_yaml(pid: str, patch: dict):
    pdir = PRODUCTS / pid
    prod_file = pdir / 'product.yaml'
    data = _load_yaml(prod_file)
    data['id'] = pid
    # 正规化映射
    mapping = {
        'name': 'name',
        'product_name': 'name',
        'product_owner': 'product_owner',
        'owner': 'product_owner',
        'intended_use': 'intended_use',
        'lifecycle_stage': 'lifecycle_stage',
        'regulatory_region': 'regulatory_region',
        'regions': 'regulatory_region',
    }
    for k, v in patch.items():
        key = mapping.get(k, k)
        if key == 'regulatory_region':
            if isinstance(v, str):
                v = [s.strip() for s in v.split(',') if s.strip()]
        data[key] = v
    _dump_yaml(prod_file, data)
    # 若 traceability 不存在则提供一个空骨架
    tfile = pdir / 'traceability.yaml'
    if not tfile.exists():
        _dump_yaml(tfile, {'baseline_version': '', 'items': []})


def main():
    if IS_ADD:
        pid = _find_line_value('产品ID（目录名')
        name = _find_line_value('产品名称')
        intended = _find_line_value('预期用途')
        owner = _find_line_value('产品负责人邮箱')
        regions = _find_line_value('注册区域')
        lifecycle = _find_line_value('生命周期阶段')
        if not pid or not name:
            raise SystemExit('表单缺少产品ID或名称')
        patch = {
            'name': name,
            'intended_use': intended or '',
            'product_owner': owner or '',
            'lifecycle_stage': lifecycle or '',
            'regulatory_region': regions or ''
        }
        upsert_product_yaml(pid, patch)

    elif IS_UPDATE:
        pid = _find_line_value('目标产品ID')
        if not pid:
            raise SystemExit('未提供产品ID')
        kv_text = _find_block_after('需要修改的字段') or ''
        patch = _parse_kv_lines(kv_text)
        upsert_product_yaml(pid, patch)

    else:
        print('非 PSMS Issue（标签不匹配），跳过')

if __name__ == '__main__':
    main()
