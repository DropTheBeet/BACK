
def query2list(query, select_cols):
    list = []
    for row in query:
        d = {}
        for column in row.__table__.columns:
            if column.name in select_cols:
                d[column.name] = str(getattr(row, column.name))
        list.append(d)
    return list