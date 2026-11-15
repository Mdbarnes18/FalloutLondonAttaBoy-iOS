PAL = dict(
    C='#4CFF7F',   # phosphor green (primary ink)
    D='#2F9E58',   # dim phosphor
    O='#7A8A3C',   # olive green
    M='#4B5A32',   # muted military green
    H='#23261F',   # charcoal
    K='#0B0D0A',   # black
    G='#7B7F73',   # industrial grey
    B='#B08D3E',   # aged brass
    A='#E3A12F',   # muted amber (warnings)
    W='#D9FFE3',   # phosphor highlight
)
def tokens(s, col=None):
    for k, v in PAL.items(): s = s.replace('@' + k, v)
    return s
