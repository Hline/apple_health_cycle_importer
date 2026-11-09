# -*- coding: utf-8 -*-
"""
Apple Health Cycle Importer - CLI 변환 스크립트
다양한 형식의 생리주기 CSV / TXT 파일을 애플 건강(iOS 단축어) 일괄 등록용 일별 날짜 형식으로 변환합니다.
"""
import csv
import json
import os
import re
import sys
from datetime import datetime, timedelta


def parse_flexible_date(date_str: str) -> datetime:
    """
    다양한 날짜 형식을 datetime으로 파싱합니다.
    지원:
      - 2026년 10월 18일
      - 2026-10-18
      - 2026.10.18
      - 2026/10/18
    """
    nums = re.findall(r"\d+", date_str.strip())
    if len(nums) < 3:
        raise ValueError(f"날짜 형식을 인식할 수 없습니다: {date_str}")
    return datetime(int(nums[0]), int(nums[1]), int(nums[2]))


def convert_cycles(input_file: str, output_txt: str = "apple_health_dates.txt", output_json: str = "apple_health_cycles.json"):
    if not os.path.exists(input_file):
        print(f"[오류] 입력 파일을 찾을 수 없습니다: {input_file}")
        return

    daily_records = {}
    cycle_count = 0

    with open(input_file, mode="r", encoding="utf-8-sig") as f:
        for line in f:
            line_str = line.strip()
            if not line_str or line_str.lower().startswith("start") or line_str.startswith("#"):
                continue

            parts = re.split(r"[,~\t]", line_str)
            if len(parts) < 2:
                continue

            try:
                start_dt = parse_flexible_date(parts[0])
                end_dt = parse_flexible_date(parts[1])
            except ValueError:
                continue

            if start_dt > end_dt:
                continue

            flow = "보통"
            if len(parts) >= 3 and parts[2].strip() in ["적음", "보통", "많음", "미지정"]:
                flow = parts[2].strip()

            cycle_count += 1
            curr = start_dt
            while curr <= end_dt:
                ymd = curr.strftime("%Y-%m-%d")
                daily_records[ymd] = {
                    "date": ymd,
                    "flow": flow,
                    "is_start": (curr == start_dt),
                }
                curr += timedelta(days=1)

    sorted_dates = sorted(daily_records.keys())
    sorted_json = [daily_records[d] for d in sorted_dates]

    with open(output_txt, mode="w", encoding="utf-8") as f:
        f.write("\n".join(sorted_dates))

    with open(output_json, mode="w", encoding="utf-8") as f:
        json.dump(sorted_json, f, ensure_ascii=False, indent=2)

    print(f"🎉 변환 완료!")
    print(f" - 총 생리 주기 횟수 : {cycle_count}회")
    print(f" - 변환된 일별 기록  : {len(sorted_dates)}일")
    print(f" - 날짜 목록 텍스트 : {output_txt}")
    print(f" - 상세 JSON 파일   : {output_json}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "sample_menstrual_cycles.csv"
    convert_cycles(target)
