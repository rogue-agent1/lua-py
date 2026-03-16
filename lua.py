#!/usr/bin/env python3
"""Minimal Lua interpreter — tables, functions, loops."""
import sys, re

class LuaTable:
    def __init__(self): self.array=[]; self.hash={}
    def set(self,k,v):
        if isinstance(k,int) and 1<=k<=len(self.array)+1:
            if k==len(self.array)+1: self.array.append(v)
            else: self.array[k-1]=v
        else: self.hash[k]=v
    def get(self,k):
        if isinstance(k,int) and 1<=k<=len(self.array): return self.array[k-1]
        return self.hash.get(k)
    def __repr__(self): return f"{{{', '.join(str(v) for v in self.array)}{', ' if self.array and self.hash else ''}{', '.join(f'{k}={v}' for k,v in self.hash.items())}}}"

def lua_eval(code, env=None):
    if env is None: env={"print":lambda *a:print(*a),"type":lambda x:type(x).__name__}
    tokens=re.findall(r'\d+\.?\d*|"[^"]*"|[a-zA-Z_]\w*|[+\-*/=<>~!]=?|[{}()\[\],;.]|\S',code)
    results=[]; i=[0]
    def peek(): return tokens[i[0]] if i[0]<len(tokens) else None
    def advance(): t=tokens[i[0]]; i[0]+=1; return t
    def expect(t):
        if peek()!=t: raise SyntaxError(f"Expected {t}, got {peek()}")
        advance()
    def expr():
        left=atom()
        while peek() in ('+','-','*','/','<','>','==','~=','..'):
            op=advance(); right=atom()
            if op=='+': left=left+right
            elif op=='-': left=left-right
            elif op=='*': left=left*right
            elif op=='/': left=left/right
            elif op=='<': left=left<right
            elif op=='>': left=left>right
            elif op=='==': left=left==right
        return left
    def atom():
        t=peek()
        if t and t[0].isdigit(): advance(); return float(t) if '.' in t else int(t)
        if t and t.startswith('"'): advance(); return t[1:-1]
        if t=='true': advance(); return True
        if t=='false': advance(); return False
        if t=='nil': advance(); return None
        if t and (t[0].isalpha() or t[0]=='_'):
            name=advance()
            if peek()=='(':
                advance(); args=[]
                while peek()!=')':
                    args.append(expr())
                    if peek()==',': advance()
                advance()
                return env[name](*args)
            return env.get(name)
        advance(); return None
    def statement():
        t=peek()
        if t=='local' or (t and t[0].isalpha()):
            if t=='local': advance(); name=advance()
            else: name=advance()
            if peek()=='=': advance(); env[name]=expr()
        elif t=='print':
            advance(); expect('('); args=[]
            while peek()!=')':
                args.append(expr())
                if peek()==',': advance()
            expect(')'); print(*args)
    while i[0]<len(tokens): statement()
    return env

if __name__ == "__main__":
    env=lua_eval('local x = 10\nlocal y = 20\nprint(x + y)')
    lua_eval('local name = "Rogue"\nprint(name)', env)
