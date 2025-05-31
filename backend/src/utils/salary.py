import re
from typing import Optional, Tuple

def parse_salary_range(salary_str: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    if not salary_str:
        return None, None, None
    salary_str = salary_str.replace("\u00a0", " ").replace("–", "-")
    pattern = re.compile(r"(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*([A-Za-z]+)")
    matches = pattern.findall(salary_str)
    if not matches:
        return None, None, None
    def to_number(s): return float(s.replace(",", ""))
    if len(matches) == 1:
        value, currency = matches[0]
        return to_number(value), to_number(value), currency
    elif len(matches) >= 2:
        value1, currency1 = matches[0]
        value2, currency2 = matches[1]
        if currency1 != currency2:
            return None, None, None
        return to_number(value1), to_number(value2), currency1
    return None, None, None
