import ast          # 코드를 '실행하지 않고' 구조(트리)로 분석하는 표준 라이브러리
import operator     # +, -, * 등을 실제 파이썬 연산으로 이어주는 표준 라이브러리

# 허용할 '이항 연산'(둘을 계산): 노드 타입 → 실제 연산 함수.
_BIN_OPS = {
    ast.Add: operator.add,        # +
    ast.Sub: operator.sub,        # -
    ast.Mult: operator.mul,       # *
    ast.Div: operator.truediv,    # /
    ast.Mod: operator.mod,        # %
    ast.Pow: operator.pow,        # **
}
# 허용할 '단항 연산'(하나에 적용): 음수(-x), 양수(+x).
_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def safe_calculate(expression: str) -> float:
    """수식 문자열을 eval 없이 계산한다. 허용되지 않은 식이면 ValueError."""
    try:
        # mode="eval": '식(expression)' 하나로 파싱. .body가 그 식의 최상위 노드.
        tree = ast.parse(expression, mode="eval").body
    except SyntaxError as exc:
        # 문법이 깨진 입력도 조용히 ValueError로 통일(밖에서 한 번에 처리).
        raise ValueError(f"수식을 해석할 수 없습니다: {expression}") from exc
    return _eval_node(tree)


def _eval_node(node: ast.AST) -> float:
    """트리 노드 하나를 재귀로 계산한다. 허용 목록에 없으면 거부."""
    # 1) 숫자 상수(3, 4.5 등)는 그대로 값.
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    # 2) 이항 연산(a + b): 좌·우를 각각 계산해 연산자로 합친다.
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        left = _eval_node(node.left)         # 왼쪽 가지 계산(재귀)
        right = _eval_node(node.right)       # 오른쪽 가지 계산(재귀)
        return _BIN_OPS[type(node.op)](left, right)
    # 3) 단항 연산(-a): 안쪽을 계산해 부호를 적용.
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_eval_node(node.operand))
    # 4) 그 외(이름·함수 호출·속성 접근 등)는 전부 거부 — 이것이 화이트리스트의 핵심.
    raise ValueError("허용되지 않은 식입니다(숫자와 사칙연산만 가능).")