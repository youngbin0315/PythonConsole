import json
import time
import os

# --- 1. 유틸리티 및 핵심 로직 ---

def mac_operation(matrix1, matrix2):
    """두 2차원 배열의 MAC(Multiply-Accumulate) 연산을 수행합니다."""
    n = len(matrix1)
    score = 0.0
    for i in range(n):
        for j in range(n):
            score += matrix1[i][j] * matrix2[i][j]
    return score

def measure_performance(matrix1, matrix2, iterations=10):
    """MAC 연산 시간을 측정합니다. (ms 반환)"""
    start_time = time.perf_counter()
    for _ in range(iterations):
        mac_operation(matrix1, matrix2)
    end_time = time.perf_counter()
    
    avg_time_sec = (end_time - start_time) / iterations
    return avg_time_sec * 1000  # ms 단위 변환

def normalize_label(label):
    """라벨을 'Cross' 또는 'X'로 정규화합니다."""
    label = str(label).strip().lower()
    if label in ['+', 'cross']:
        return 'Cross'
    elif label in ['x']:
        return 'X'
    return label

def compare_scores(score_a, score_b, label_a="A", label_b="B", epsilon=1e-9):
    """허용오차(epsilon)를 적용하여 점수를 비교하고 결과를 반환합니다."""
    if abs(score_a - score_b) < epsilon:
        return "UNDECIDED"
    return label_a if score_a > score_b else label_b

def input_matrix(name, size=3):
    """콘솔에서 행렬을 입력받고 검증합니다."""
    print(f"\n[{name}] {size}x{size} 행렬을 한 줄씩 공백으로 구분하여 입력하세요.")
    matrix = []
    while len(matrix) < size:
        try:
            row_str = input(f"행 {len(matrix) + 1}: ")
            row = [float(x) for x in row_str.split()]
            if len(row) != size:
                print(f"입력 형식 오류: 정확히 {size}개의 숫자를 입력해야 합니다. 다시 입력해주세요.")
                continue
            matrix.append(row)
        except ValueError:
            print("입력 형식 오류: 숫자만 입력 가능합니다. 다시 입력해주세요.")
    return matrix


# --- 2. 모드 1: 사용자 입력 모드 (3x3) ---

def mode_user_input():
    print("\n=== [모드 1] 사용자 입력 모드 (3x3) ===")
    filter_a = input_matrix("필터 A", 3)
    filter_b = input_matrix("필터 B", 3)
    pattern = input_matrix("입력 패턴", 3)

    score_a = mac_operation(pattern, filter_a)
    score_b = mac_operation(pattern, filter_b)
    
    # 성능 측정 (10회 반복)
    avg_time = measure_performance(pattern, filter_a, 10)
    
    result = compare_scores(score_a, score_b, "A", "B")

    print("\n--- 결과 ---")
    print(f"필터 A MAC 점수: {score_a:.4f}")
    print(f"필터 B MAC 점수: {score_b:.4f}")
    print(f"판정 결과: {result}")
    
    print("\n--- 성능 분석 (3x3) ---")
    print(f"{'크기':<10} | {'평균 시간(ms)':<15} | {'연산 횟수(N²)'}")
    print("-" * 45)
    print(f"{'3x3':<10} | {avg_time:<15.6f} | {3**2}")


# --- 3. 모드 2: JSON 로드 및 분석 모드 ---

def mode_json_analysis():
    print("\n=== [모드 2] JSON 데이터 분석 모드 ===")
    if not os.path.exists('data.json'):
        print("오류: 'data.json' 파일을 찾을 수 없습니다.")
        return

    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    filters = data.get('filters', {})
    patterns = data.get('patterns', {})

    total_cases = len(patterns)
    pass_count = 0
    fail_count = 0
    failed_cases = []
    perf_data = {}

    print(f"총 {total_cases}개의 패턴을 분석합니다...\n")

    for pat_key, pat_data in patterns.items():
        input_pattern = pat_data.get('input', [])
        raw_expected = pat_data.get('expected', '')
        expected_label = normalize_label(raw_expected)

        try:
            size_n = int(pat_key.split('_')[1])
        except (IndexError, ValueError):
            failed_cases.append((pat_key, "키 형식 오류 (크기 추출 불가)"))
            fail_count += 1
            continue

        filter_group = filters.get(f"size_{size_n}", {})
        if not filter_group:
            failed_cases.append((pat_key, f"size_{size_n} 필터를 찾을 수 없음"))
            fail_count += 1
            continue
            
        if len(input_pattern) != size_n or any(len(row) != size_n for row in input_pattern):
            failed_cases.append((pat_key, f"패턴 스키마 오류 (크기 {size_n}x{size_n} 불일치)"))
            fail_count += 1
            continue

        cross_filter = None
        x_filter = None
        for f_key, f_matrix in filter_group.items():
            norm_key = normalize_label(f_key)
            if norm_key == 'Cross': cross_filter = f_matrix
            elif norm_key == 'X': x_filter = f_matrix

        if not cross_filter or not x_filter:
            failed_cases.append((pat_key, "정규화된 Cross 또는 X 필터를 찾을 수 없음"))
            fail_count += 1
            continue

        score_cross = mac_operation(input_pattern, cross_filter)
        score_x = mac_operation(input_pattern, x_filter)
        decision = compare_scores(score_cross, score_x, "Cross", "X")

        is_pass = (decision == expected_label)
        if is_pass:
            pass_count += 1
        else:
            fail_count += 1
            failed_cases.append((pat_key, f"판정 실패 (Expected: {expected_label}, Got: {decision})"))

        avg_t = measure_performance(input_pattern, cross_filter, 10)
        if size_n not in perf_data:
            perf_data[size_n] = []
        perf_data[size_n].append(avg_t)

        print(f"[{pat_key}] Cross: {score_cross:8.2f} | X: {score_x:8.2f} | 판정: {decision:10} | 결과: {'PASS' if is_pass else 'FAIL'}")

    print("\n--- 성능 분석 (크기별 MAC 연산) ---")
    print(f"{'크기(NxN)':<10} | {'평균 시간(ms)':<15} | {'연산 횟수(N²)'}")
    print("-" * 45)
    
    for size in sorted(perf_data.keys()):
        overall_avg = sum(perf_data[size]) / len(perf_data[size])
        print(f"{f'{size}x{size}':<10} | {overall_avg:<15.6f} | {size**2}")

    print("\n=== [결과 리포트] ===")
    print(f"전체 테스트 수: {total_cases}")
    print(f"통과 수: {pass_count}")
    print(f"실패 수: {fail_count}")

    if fail_count > 0:
        print("\n[실패 케이스 목록]")
        for case, reason in failed_cases:
            print(f" - {case}: {reason}")
    else:
        print("\n[알림] 모든 케이스를 성공적으로 통과했습니다.")


# --- 메인 실행 흐름 ---

def main():
    while True:
        try:
            print("\n==================================")
            print("  MAC 패턴 매칭 테스트 프로그램  ")
            print("==================================")
            print("1. 사용자 입력 모드 (3x3)")
            print("2. JSON 데이터 분석 모드 (data.json)")
            print("3. 종료")
            choice = input("원하는 모드를 선택하세요 (1/2/3): ")

            if choice == '1':
                mode_user_input()
            elif choice == '2':
                mode_json_analysis()
            elif choice == '3':
                print("프로그램을 종료합니다.")
                break
            else:
                print("잘못된 입력입니다. 다시 선택해주세요.")
                
        # Ctrl+C 예외 처리 추가
        except KeyboardInterrupt:
            print("\n\n[알림] 강제 종료(Ctrl+C)가 감지되어 프로그램을 안전하게 종료합니다.")
            break
        except EOFError:
            print("\n\n[알림] 입력 스트림이 종료되었습니다.")
            break

if __name__ == "__main__":
    main()