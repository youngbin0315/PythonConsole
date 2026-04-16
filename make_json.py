import json

def make_matrix(size, pattern_type):
    """간단한 Cross(+) 또는 X 모양의 행렬을 생성합니다."""
    matrix = [[0]*size for _ in range(size)]
    mid = size // 2
    for i in range(size):
        if pattern_type == 'cross':
            matrix[mid][i] = 1
            matrix[i][mid] = 1
        elif pattern_type == 'x':
            matrix[i][i] = 1
            matrix[i][size - 1 - i] = 1
    return matrix

sizes = [3, 5, 13, 25]
data = {"filters": {}, "patterns": {}}

# 필터 생성
for s in sizes:
    data["filters"][f"size_{s}"] = {
        "cross": make_matrix(s, 'cross'),
        "x": make_matrix(s, 'x')
    }

# 패턴 생성 (PASS 케이스들)
for s in sizes:
    data["patterns"][f"size_{s}_1"] = {
        "input": make_matrix(s, 'cross'),
        "expected": "+"
    }
    data["patterns"][f"size_{s}_2"] = {
        "input": make_matrix(s, 'x'),
        "expected": "x"
    }

# 실패(FAIL) 로직 검증용 에러 케이스 1개 추가
data["patterns"]["size_5_error"] = {
    "input": [[1,1], [1,1]], 
    "expected": "x"
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("성공적으로 data.json 파일이 생성되었습니다! 이제 main.py를 실행하세요.")