"""

Projet Compilateur HTML - Interpreter
Milan Cervino & William Bikuta
22.11.2021 - 14.01.2022

"""

import Node
from Node import addToClass

vars = {}

@addToClass(Node.Node)
def show(self, tabs=0):
    
    # Fonction show parente par defaut
    
    output = ""
        
    # Si la balise a un contenu texte non nul
    if self.content != "":
        
        text = self.content
        
        # Si le contenu contient le symbole '%' (alors il y une variable a interprete)
        if "%" in self.content:
            
            # Isole le nom de la variable
            v = self.content.split("%", 1)[1].split(" ", 1)[0]
            
            # Si la variable existe et est instancie, alors inclu sa valeur dans le contenu
            if v in vars:
                text = self.content.replace("%" + v, str(vars[v]))
                
        output += text + "\n"
    
    # Appelle la methode show de chaque enfant de la balise
    for i in self.children:
        if i is not None:
            output += i.show(tabs)
        
    return output

@addToClass(Node.TokenNode)
def show(self, tabs=0):
    output = ""
    
    # Incremente la tabulation pour un affichage plus propre et un code indente
    for i in range(tabs): 
        output += "\t"
        
    # Appelle la methode show de la classe parente
    output += super(Node.TokenNode, self).show(tabs)
    
    return output

@addToClass(Node.AssignNode)
def show(self, tabs=0):
    
    output = ""
    
    # Incremente la tabulation pour un affichage plus propre et un code indente
    for i in range(tabs): 
        output +=  "\t"
        
    # Si l'attribut existe et est complet (nom + valeur), alors on l'integre dans la balise
    if (self.attribute is not None and self.attribute[0] is not None and self.attribute[1] is not None): 
        output += "<" + self.balise + " style=\"" + self.attribute[0][0]
        output += ":" + self.attribute[1] + ";\"" + ">\n"
    else:
        output += "<" + self.balise + ">\n"
           
    # Appelle la methode show de la classe parente
    output += super(Node.AssignNode, self).show(tabs+1)
        
    # Incremente la tabulation pour un affichage plus propre et un code indente
    for i in range(tabs):
        output+= "\t"
        
    # Fermeture de la balise
    output += "</" + self.balise + ">\n"
        
    return output

@addToClass(Node.IfNode)
def show(self, tabs=0):
    output = ""
    
    # Couleur css par defaut
    value = self.condition[0][1]

    # Si l'attribut parent est le même que l'attrbut teste, alors on recupere
    # sa valeur, sinon la valeur par defaut de la'ttrbut est preserve
    if self.parentAttr[0][0] == self.condition[0][0]:
        value = self.parentAttr[1]
        
    cond = True
            
    # Si la condition n'est pas inverse par un "is not"
    if self.isnot is False:
        cond = value == str.replace(self.condition[1], '\"', '')
    else:
        cond = value != str.replace(self.condition[1], '\"', '')
                
    # Si la condition est respecte, affiche le contenu du bloc if, sinon du bloc else
    if cond:
        output += self.blocIF.show(tabs)
    else:
        if(self.blocELSE != None):
            output += self.blocELSE.show(tabs)
        
    return output

@addToClass(Node.ForNode)
def show(self, tabs = 0):
    output = ""

    # itere dans l'intervalle [start, end]
    for i in range(self.start, self.end+1):
        # modifie la variable i
        vars[self.var] = i
        output += self.block.show(tabs)
        
    # supprime la variable du dictionnaire
    vars.pop(self.var, None)
        
    return output

if __name__ == '__main__':
    
    import sys
    from parserHiComp import parse
    
    prog = open(sys.argv[1]).read()
    node = parse(prog)
    
    output = "<!DOCTYPE html>\n<html>\n"
    output += node.show(1)
    output += "\n</html>"
    print(output)
    
    # Add in html file
    html_file = open("output/test.html", "w")
    html_file.write(output)
    html_file.close()