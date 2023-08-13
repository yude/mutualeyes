def auto_decode(query: bytes, encoding=['utf8', 'cp1252']):
    for i in encoding:
        try:
            return query.decode(i)
        except UnicodeDecodeError:
            pass
