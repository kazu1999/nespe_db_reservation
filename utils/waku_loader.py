import json
import os
import re
from typing import Dict, Any


def _parse_system_properties(system_properties_path: str) -> Dict[int, Dict[str, Any]]:
    patterns: Dict[int, Dict[str, Any]] = {}
    if not os.path.exists(system_properties_path):
        return patterns

    name_re = re.compile(r"^\$WAKUPATTERN\[(\d+)\]\['Name'\]\s*=\s*\"(.*)\";")
    st_re = re.compile(r"^\$WAKUPATTERN\[(\d+)\]\['StartTime'\]\[(\d+)\]\s*=\s*\"(.*)\";")
    et_re = re.compile(r"^\$WAKUPATTERN\[(\d+)\]\['EndTime'\]\[(\d+)\]\s*=\s*\"(.*)\";")
    ampm_re = re.compile(r"^\$WAKUPATTERN\[(\d+)\]\['AMPM'\]\[(\d+)\]\s*=\s*\"(.*)\";")
    jt_re = re.compile(r"^\$WAKUPATTERN\[(\d+)\]\['JikanTani'\]\s*=\s*\"(\d+)\";")

    with open(system_properties_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            m = name_re.match(line)
            if m:
                idx = int(m.group(1))
                patterns.setdefault(idx, {})['Name'] = m.group(2)
                if 'StartTime' not in patterns[idx]:
                    patterns[idx]['StartTime'] = []
                if 'EndTime' not in patterns[idx]:
                    patterns[idx]['EndTime'] = []
                if 'AMPM' not in patterns[idx]:
                    patterns[idx]['AMPM'] = []
                continue

            m = st_re.match(line)
            if m:
                idx = int(m.group(1)); pos = int(m.group(2)); val = m.group(3)
                patterns.setdefault(idx, {}).setdefault('StartTime', [])
                lst = patterns[idx]['StartTime']
                if len(lst) <= pos:
                    lst.extend([None] * (pos - len(lst) + 1))
                lst[pos] = val
                continue

            m = et_re.match(line)
            if m:
                idx = int(m.group(1)); pos = int(m.group(2)); val = m.group(3)
                patterns.setdefault(idx, {}).setdefault('EndTime', [])
                lst = patterns[idx]['EndTime']
                if len(lst) <= pos:
                    lst.extend([None] * (pos - len(lst) + 1))
                lst[pos] = val
                continue

            m = ampm_re.match(line)
            if m:
                idx = int(m.group(1)); pos = int(m.group(2)); val = m.group(3)
                patterns.setdefault(idx, {}).setdefault('AMPM', [])
                lst = patterns[idx]['AMPM']
                if len(lst) <= pos:
                    lst.extend([None] * (pos - len(lst) + 1))
                lst[pos] = val
                continue

            m = jt_re.match(line)
            if m:
                idx = int(m.group(1)); val = m.group(2)
                patterns.setdefault(idx, {})['JikanTani'] = val
                continue

    for p in patterns.values():
        for key in ('StartTime', 'EndTime', 'AMPM'):
            if key in p and isinstance(p[key], list):
                p[key] = [x for x in p[key] if x is not None]
    return patterns


def load_waku_patterns(config_path: str = None, system_properties_path: str = None) -> Dict[int, Dict[str, Any]]:
    """
    枠パターン定義をロードする。
    優先順位: JSONコンフィグ > system.properties パース > 空の辞書
    """
    if config_path is None:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'waku_patterns.json')
    if system_properties_path is None:
        system_properties_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'system.properties')

    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                patterns: Dict[int, Dict[str, Any]] = {int(k): v for k, v in data.items()}
                return patterns
    except Exception:
        pass

    try:
        parsed = _parse_system_properties(system_properties_path)
        if parsed:
            return parsed
    except Exception:
        pass

    return {}


if __name__ == "__main__":
    # 簡易テスト: 設定ファイルから読み込み、サマリーを出力
    cfg = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'waku_patterns.json')
    sysprop = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'system.properties')

    patterns = load_waku_patterns(cfg, sysprop)
    count = len(patterns)
    print(f"パターン数: {count}")
    # 先頭の数件のみダイジェスト表示
    for pid in sorted(patterns.keys())[:5]:
        p = patterns[pid]
        name = p.get('Name')
        st = p.get('StartTime', [])
        et = p.get('EndTime', [])
        ampm = p.get('AMPM', [])
        print({
            'id': pid,
            'Name': name,
            'StartTime': st,
            'EndTime': et,
            'AMPM': ampm,
        })
