
# 쿼리 결과를 선택한 속성만 추출하여 리스트로 반환
def query2list(query, select_cols=None):
    list = []
    for row in query:
        list.append(row.as_dict(select_cols))
    return list