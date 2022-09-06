"""

Projet Compilateur HTML  - Lexer
Milan Cervino & William Bikuta
22.11.2021 - 14.01.2022

Analyse lexical du compilateur

"""

import ply.lex as lex

reserved_words = (
        'if',
        'else',
        'for',
        'to',
        'is',
        'not'
)


tokens = (
    'NUMBER',
    'STRING',
    'IDENTIFIER',
) + tuple(map(lambda s:s.upper(), reserved_words))


# caracteres acceptes
literals = '();={}\'"\.\-'


def t_NUMBER(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r'(\"(.+?)\") | (\'(.+?)\')'
    t.value = str(t.value)
    return t

def t_IDENTIFIER(t):
    r'[A-Za-z_]\w*'
    if t.value in reserved_words:
        t.type = t.value.upper()
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


t_ignore = ' \t'

def t_error(t):
    print("IllegalCharacter '%s'"%t.value[0])
    t.lexer.skip(1)
    

lex.lex()


if __name__ == "__main__":
    import sys
    prog = open(sys.argv[1]).read()
    
    lex.input(prog)

    while 1:
        tok = lex.token()
        if not tok: break
        print("line %d: %s(%s)"%(tok.lineno, tok.type, tok.value))