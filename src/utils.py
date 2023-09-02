import mip

def auto_decode(query: bytes, encoding=['utf8', 'cp1252']):
    for i in encoding:
        try:
            return query.decode(i)
        except UnicodeDecodeError:
            pass

def enum(**enums: int):
    return type('Enum', (), enums)

def install_dependencies():
    mip.install("copy")
