"""

Projet Compilateur HTML - Parser
Milan Cervino & William Bikuta
22.11.2021 - 14.01.2022

"""

import ply.yacc as yacc
import Node
from lexer import tokens

# colors permet de recuperer les composants RGB des couleurs CSS
from matplotlib import colors
import math

# balise : Nom de la balise HTML
balise = {
    'header1':'h1',
    'header2':'h2',
    'body':'body',
    'head':'head',
    'title':'title',
    'text' : 'p',
    'list' : 'ul',
    'element' : 'li',
    'div' : 'div'
}

# attribute: [attribut css, valeur par defaut]
attribute = {
    'backgroundcolor': ['background-color', 'white'], 
    'color': ['color', 'black']
}

# Pile des couleurs
colorStack = []

# Compte le nombre de IF actifs 
if_active = 0

def p_programme(p):
    """programme : statement
        | statement programme"""        
    try:
        p[0] = Node.ProgramNode(children=[p[1]] + p[2].children)
    except:
        p[0] = Node.ProgramNode(children=p[1])

def p_statement(p):
    """statement : assignation
        | structure"""
    p[0] = p[1]
    
    
def p_structure(p):
    """structure : condition
        | loop"""
    p[0] = p[1]
    
def p_condition(p):
    """condition : if '(' parameter IS STRING ')' bloc 
        | if '(' parameter IS STRING ')' bloc ELSE bloc
        | if '(' parameter IS NOT STRING ')' bloc
        | if '(' parameter IS NOT STRING ')' bloc ELSE bloc"""
        
    # Si l'utilisateur a inverse la condition
    if p[5] == 'not':
        try:    
            p[0] = Node.IfNode([p[3], p[6]], p[8], p[10], lastColor(), isnot=True)
        except:
            p[0] = Node.IfNode([p[3], p[6]], p[8], parentAttr=lastColor(), isnot=True)
    else:
        try:    
            p[0] = Node.IfNode([p[3], p[5]], p[7], p[9], lastColor())
        except:
            p[0] = Node.IfNode([p[3], p[5]], p[7], parentAttr=lastColor())
        
    # Decremente le nombre de if actifs car on sort du IF
    global if_active
    if_active -= 1
            
def p_if(p):
    """if : IF"""
    
    # Incremente le nombre de if actifs car on entre dans un IF
    global if_active
    if_active += 1
    p[0] = p[1]
        
def p_loop(p):
    """loop : FOR '(' IDENTIFIER '=' NUMBER TO NUMBER ')' bloc"""
    
    # Si valeur de depart > valeur arrivee, alors erreur
    if p[5] > p[7]:
        print(f"Error: start number cannot be greater than end number in for loop")
    else:  
        p[0] = Node.ForNode(p[3], p[5], p[7], p[9])

def p_assign(p):
    """assignation : IDENTIFIER content
        | IDENTIFIER attribute content """
      
    # Si la balise n'est pas repertoriee dans le dictionnaire, alors erreur     
    if p[1] not in balise:
        print(f"Error: element {p[1]} does not exist in dictionnary")
    else: 
        try:
            p[0] = Node.AssignNode(balise[p[1]], p[3], attribute=p[2])
            
            # si il y a une valeur dans la pile, alors on sort la derniere
            if colorStack:
                colorStack.pop()
    
        # Dans le cas ou il n'y a pas d'attribut
        except:
            p[0] = Node.AssignNode(balise[p[1]], p[2])
            
            # Recupere la derniere couleur inseree dans la pile
            t = lastColor()
            
            # Test sur la couleur pour savoir si l'affichage sera lisible
            # Si la balise se trouve dans un IF, alors if_active > 0
            # if_active permet de protéger les balises dans les if
            if t[0][0] == "background-color" and t[1] == "black" and if_active == 0:
                print("Warning text not visible")

def p_attribute(p):
    """attribute : parameter '=' STRING"""
    
    # On remplace tous les guillements par rien
    value = p[3].replace('\"', '')
    
    distance = True
    
    # Si le parametre n'est pas nul
    if p[1] is not None:
        
        # Si le parametre est une couleur et n'est pas dans un if
        if p[1][0] == "background-color" or p[1][0] == "color" and if_active == 0:
                
            # Alors on recupere la derniere couleur
            t = lastColor()
                
            # Si la couleur est la meme que la couleur de fond, alors warning
            if t[0][0] == "background-color" and t[1] == value:
                print(f"Warning text not visible, {value} background")
            else:
                # Recupere distance
                distance = color_distance(value, t[1])
                
                # Si distance n'est pas nul (si la couleur existe)
                if distance is not None:
                    # Si distance n'est pas accepte
                    if distance is False:
                        print(f"Warning color hardly visible, colors are too similar {value} and {t[1]}")
    
    # Si distance n'est pas nul (si la couleur existe)
    if distance is not None:
        p[0] = [p[1], value]
        
        # Ajout de la couleur dans la pile
        colorStack.append(p[0])

def p_parameter(p):
    """parameter : IDENTIFIER"""
    
    # Si l'attribut n'est pas repertorie dans le dictionnaire, alors erreur
    if p[1].replace('\"', '') not in attribute:
        print(f"Error: attribute {p[1]} does not exist in dictionnary")
    else:
        p[0] = attribute[p[1].replace('\"', '')]

def p_content(p):
    """content : bloc
        | element"""
    p[0] = p[1]

def p_bloc(p):
    """bloc : '{' programme '}' """

    p[0] = Node.BlockNode(Node.ProgramNode(p[2]))

def p_element(p):
    """element : expression ';'"""
    
    p[0] = p[1] 

def p_expression_num(p):
    """expression : NUMBER"""
    p[0] = Node.TokenNode(p[1])

def p_expression_string(p):
    """expression : STRING"""
    p[0] = Node.TokenNode(p[1].replace('\"', ''))

def p_error(p):
    print("Syntax errorline %d" % p.lineno)
    yacc.errok()
    
# Retourne la derniere couleur de la pile si elle existe
def lastColor():
    
    # si la pile n'est pas vide retourne la derniere valeur
    if colorStack:
        return colorStack[-1]
    
    # sinon retourne un valeur par defaut
    else:
        return [attribute["backgroundcolor"], attribute["backgroundcolor"][1]]
    
# Retourne Vrai si la distance entre les couleurs est suffisamment grande
def color_distance(currentColor, parentColor):
    
    # Test si la couleur CSS existe et recupere les composantes rgb
    try:
        rgb1 = colors.to_rgb(currentColor)
    except:
        print(f"Warning {currentColor} color does not exist")
        return None
    
    # Test si la couleur CSS existe et recupere les composantes rgb
    try:
        rgb2 = colors.to_rgb(parentColor)
    except:
        rgb2 = colors.to_rgb("black")
    
    # source = https://en.wikipedia.org/wiki/Color_difference
    
    # calcul de la distance entre les deux couleurs
    distance = math.sqrt((rgb1[0]-rgb2[0])**2 + (rgb1[1]-rgb2[1])**2 + (rgb1[2]-rgb2[2])**2)
    
    # Si la distance est inferieur au seuil
    # Ici le seuil est une taille arbitraire elle peut augmenter si on veut etre plus strict
    # ou diminuer pour etre plus souple
    if distance <= 0.15:
        return False
    else:
        return True

yacc.yacc(outputdir="generated")

def parse(program):
    return yacc.parse(program)

if __name__ == "__main__":
    
    import sys
    prog = open(sys.argv[1]).read()
    node = parse(prog) 
    
    graph = node.makegraphicaltree()
    name = 'output/ast.pdf'
    graph.write_pdf(name)
    print('wrote ast to', name)
    