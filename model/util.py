
def query2list(query, select_cols=None):
    list = []
    for row in query:
        list.append(row.as_dict(select_cols))
    return list