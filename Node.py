"""

Projet Compilateur HTML - Node
Milan Cervino & William Bikuta
22.11.2021 - 14.01.2022

"""

import pydot

lastAttribute = []

class Node:
    content = ""
    children = []
    type = 'Node (unspecified)'
    shape = 'ellipse'
    count = 0
    
    def __init__(self, children = None, content = "", parentAttr=None):
        self.content = content
        
        self.ID = str(Node.count)
        Node.count+=1
        
        if not children:
            self.children = []
        
        # Si il y plusieurs enfants (children est une liste)
        elif hasattr(children, '__len__'):
            self.children = children
        else:
            self.children = [children]
        
        self.parentAttr= parentAttr

    def addNext(self, next):
        self.next.append(next)        
       
    def __iter__(self):
        return iter(self.children)
    
    def __repr__(self):
        return self.type
    
    def asciitree(self, prefix=''):
        result = "%s%s\n" % (prefix, repr(self))
        prefix += '|  '
        for c in self.children:
            if not isinstance(c,Node):
                result += "%s*** Error: Child of type %r: %r\n" % (prefix,type(c),c)
                continue
            result += c.asciitree(prefix)
        return result
    
    def makegraphicaltree(self, dot=None, edgeLabels=True):
        if not dot: dot = pydot.Dot()
        dot.add_node(pydot.Node(self.ID,label=repr(self), shape=self.shape))
        label = edgeLabels and len(self.children)-1
        for i, c in enumerate(self.children):
            if c is not None:
                c.makegraphicaltree(dot, edgeLabels)
                edge = pydot.Edge(self.ID,c.ID)
                if label:
                    edge.set_label(str(i))
                dot.add_edge(edge)
                #Workaround for a bug in pydot 1.0.2 on Windows:
                #dot.set_graphviz_executables({'dot': r'C:\Program Files (x86)\Graphviz2.38\bin\dot.exe'})
        return dot
        
    def threadTree(self, graph, seen = None, col=0):
        colors = ('red', 'green', 'blue', 'yellow', 'magenta', 'cyan')
        if not seen: seen = []
        if self in seen: return
        seen.append(self)
        new = not graph.get_node(self.ID)
        if new:
            graphnode = pydot.Node(self.ID,label=repr(self), shape=self.shape)
            graphnode.set_style('dotted')
            graph.add_node(graphnode)
        label = len(self.next)-1
        for i,c in enumerate(self.next):
            if not c: return
            col = (col + 1) % len(colors)
            #color = colors[col] 
            color = colors[0] 
            c.threadTree(graph, seen, col)
            edge = pydot.Edge(self.ID,c.ID)
            edge.set_color(color)
            edge.set_arrowsize('.5')
            # Les arrêtes correspondant aux coutures ne sont pas prises en compte
            # pour le layout du graphe. Ceci permet de garder l'arbre dans sa représentation
            # "standard", mais peut provoquer des surprises pour le trajet parfois un peu
            # tarabiscoté des coutures...
            # En commantant cette ligne, le layout sera bien meilleur, mais l'arbre nettement
            # moins reconnaissable.
            edge.set_constraint('false') 
            if label:
                edge.set_taillabel(str(i))
                edge.set_labelfontcolor(color)
            graph.add_edge(edge)
        return graph    
        
class ProgramNode(Node):
    type = 'Program'
    
    def __init__(self, children, parentAttr=None):
        Node.__init__(self, children=children, parentAttr=parentAttr)
        
    
class TokenNode(Node):
    type = 'token'
    
    def __init__(self, tok, parentAttr=None):
        Node.__init__(self, content=tok, parentAttr=parentAttr)

class AssignNode(Node):
    type = 'assign'
    
    def __init__(self, balise, content, attribute=None, parentAttr=None):
        self.balise = balise
        self.attribute = attribute
        Node.__init__(self, children=content,parentAttr=parentAttr)

class BlockNode(Node):
    type = 'block'
    
    def __init__(self, block, parentAttr=None):
        Node.__init__(self, children=block.children ,parentAttr=parentAttr)
        
        
class IfNode(Node):
    type = 'if'
    
    def __init__(self, condition, blocIF, blocELSE=None, parentAttr=None, isnot=False):
        self.condition = condition
        self.blocIF = blocIF
        self.blocELSE = blocELSE
        self.isnot = isnot
        
        if blocELSE is not None:
            Node.__init__(self, children=[blocIF, blocELSE],parentAttr=parentAttr)
        else:
            Node.__init__(self, children=blocIF,parentAttr=parentAttr)
    
class ForNode(Node):
    type = 'for'
    
    def __init__(self, var, start, end, block):
        self.var = var
        self.start = start
        self.end = end
        self.block = block
        Node.__init__(self, children=block)
    
def addToClass(cls):
    ''' Décorateur permettant d'ajouter la fonction décorée en tant que méthode
    à une classe.
    
    Permet d'implémenter une forme élémentaire de programmation orientée
    aspects en regroupant les méthodes de différentes classes implémentant
    une même fonctionnalité en un seul endroit.
    
    Attention, après utilisation de ce décorateur, la fonction décorée reste dans
    le namespace courant. Si cela dérange, on peut utiliser del pour la détruire.
    Je ne sais pas s'il existe un moyen d'éviter ce phénomène.
    '''
    def decorator(func):
        setattr(cls,func.__name__,func)
        return func
    return decorator