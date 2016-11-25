'''
Created on Jul 10, 2014

@author: lorenzo
'''

import copy

class Tree:
    def __init__(self, root = None, children = None, string = None, lexicalized=False):
        if string is None:
            self.root = root
            self.children = children

        else:
            self.parse(string)
            self.cleanup()

        if lexicalized:
            self.lexicalized()

        self.string = string
        self.sentence = self.sentence_()
        self.lexicalized = lexicalized
        self.taggedSentence = self.sentence_(posTag=True)

    def cleanup(self):
        #t = Tree()
        for i in self.allNodes():
            i.root = i.root.strip(")")
            if not i.isTerminal():
                if i.children[0] == "":
                    i.children = None

        return self

    @staticmethod
    def biggestPars(s):
        count = 0
        pars = []
        for position, char in enumerate(s):
            if char == "(":
                count = count + 1
                if count == 1:
                    startPos = position
            if char == ")":
                count = count - 1
                if count == 0 and position != 0:
                    endPos = position
                    pars.append(s[startPos:endPos+1])

        return pars

    def parse(self, string):
        p = Tree.biggestPars(string)

        if len(p) == 1:
            if p[0].count("(") == 1 and p[0].count(")") == 1:
                root, _, child = p[0].partition(" ")
                self.root = root[1:]
                self.children = [Tree(root = child[:-1])]

            else:
                root, _, rest = p[0].partition(" ")
                children = []
                self.root = root[1:]

                for c in Tree.biggestPars(rest):
                    #nt = parse(c)
                    nt = Tree(string=c)
                    children.append(nt)
                self.children = children

    def __eq__(self, other):
        return self.__str__() == other.__str__()

    def __hash__(self):
        return hash(self.__str__())

    def __str__(self):
        if self.isTerminal():
            #print (self.root.left)
            return self.root
        if self.isPreTerminal():
            #return "(" + self.root + " " + self.children[0].root + ")"
            return "(" + self.root + " " + " ".join(c.__str__() for c in self.children) + ")"
            #return self.root + " (" + " ".join(c.__helper_str__() for c in self.children) + ")"

        else:
            return "(" + self.root + " " + " ".join(c.__str__() for c in self.children) + ")"
            #return self.root + " (" + " ".join(c.__helper_str__() for c in self.children) + ")"

    def __repr__(self):
        return self.__str__()
    #def __str__(self):
    #    return "(" + self.__helper_str__() + ")"


    # def __str__(self):
    #     if self.isTerminal():
    #         return self.root
    #     if self.isPreTerminal():
    #         return self.root + " -> " + " , ".join(str(c) for c in self.children)
    #
    #     else:
    #         return self.root + " -> {" +  " , ".join(str(c) for c in self.children) + "}"

    def isTerminal(self):
        return self.children is None

    def isPreTerminal(self):
        if self.children is None:
            return False
        else:
            return all(c.isTerminal() for c in self.children)

    def hasSingleProduction(self):
        for n in self.allNodes():
            if not (n.isPreTerminal() or n.isTerminal()):
                if len(n.children) == 1:
                    return True
        return False

    def singleNode(self):
        if not (self.isPreTerminal() or self.isTerminal()):
            if len(self.children) == 1:
                return True
        return False

#     def binarize(self):
#         if not self.hasSingleProduction():
#             return self
#         for n in self.allNodes():
#             if n.singleNode():
#                 subtrees = n.children[0].children
#                 n.children = subtrees
#         return self

    def binarize(self):
        while self.singleNode():
            subtrees = self.children[0].children
            self.children = subtrees
        if not self.isPreTerminal():
            for sub in self.children:
                sub.binarize()
        return self

    #SBAGLIATA
    def debinarize(self):
        if not self.isPreTerminal():
            if self.root.startswith("@"):
                return self.debinarize_list(self.children)
            else:
                self.children = self.debinarize_list(self.children)
        return [self]

    def debinarize_list(self,list_of_trees):
        new_list = []
        for t in list_of_trees:
            new_list = new_list + t.debinarize()
        return new_list

    def normalize(self):
        for n in self.allTerminalNodes():
            n.root = n.root.lower()
        return self


    def allNodes(self):
        yield self
        if not self.isTerminal():
            for c in self.children:
                yield from c.allNodes()

    def allTerminalNodes(self):
        for n in self.allNodes():
            if n.isTerminal():
                yield n
            else:
                continue

    def topRule(self):
        if not self.isTerminal():
            children = [Tree(x.root,None) for x in self.children]
            return Tree(self.root, children)


    def allRules(self):
        for node in self.allNodes():
            if not node.isTerminal():
                children = [Tree(x.root,None) for x in node.children]
                t = Tree(node.root, children)
                t.terminalRule = node.isPreTerminal()
                yield t

    def sentence_(self, posTag=False):
        # if False:
        #     #print (123)
        #     return " ".join([n.root for n in self.allNodes() if n.isTerminal()])
        # else:
        if posTag:
            l = [(n.root, n.children[0].root) for n in self.allNodes() if n.isPreTerminal()]
            return l
        else:
            l = [n.root for n in self.allNodes() if n.isTerminal()]
            if l != [None]:
                return " ".join(l)
            else:
                return None

    def span(self):
        l = [n.root for n in self.allNodes() if n.isTerminal()]
        if l != [None]:
            return l
        else:
            return None



    def depth(self):
        if self.isTerminal():
            return 1
        else:

            return (1 + max(c.depth() for c in self.children))

    def lexicalized(self):
        for n in self.allNodes():
            if n.isTerminal():
                n.lemma = n.root
            else:
                s = n.root.split("#")
                n.root = s[0]
                n.lemma = s[1].split(":")[0].replace("$", "::")

    def add(self, child, position):
        tt = copy.deepcopy(self)
        for i, n in enumerate(tt.allTerminalNodes()):
            if position == i:
                #magari controllare che le root coincidano
                n.children = child.children

        return tt


    def removeWords(self):
        tt = copy.deepcopy(self)
        for n in tt.allNodes():
            if n.isPreTerminal():
                n.children = None

        return tt


if __name__ == "__main__":
    treeString4 = "(S (@S (@S (@S (INTJ no) (, ,)) (NP it)) (VP (@VP (VBD was) (RB n't)) (NP (NNP black) (NNP monday)))) (. .))"
    t = Tree(string=treeString4)
    print (t)
    tt = t.removeWords()
    print (tt)
    print ('---')
    for n in tt.allNodes():
        print (n.root, n.children)
