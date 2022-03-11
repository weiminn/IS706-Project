#-*-coding:utf-8-*-
def isAbstract(m):
    return (m & 1024) != 0

def isInterface(m):
    return (m & 512) != 0

def isNative(m):
    return (m & 256) != 0

def isPrivate(m):
    return (m & 2) != 0

def isProtected(m):
    return (m & 4) != 0

def isPublic(m):
    return (m & 1) != 0

def isStatic(m):
    return (m & 8) != 0

def isSynchronized(m):
    return (m & 32) != 0

def isTransient(m):
    return (m & 128) != 0

def isVolatile(m):
    return (m & 64) != 0

def isStrictFP(m):
    return (m & 2048) != 0

def isAnnotation(m):
    return (m & 8192) != 0

def isEnum(m):
    return (m & 16384) != 0

def isSynthetic(m):
    return (m & 4096) != 0

def isConstructor(m):
    return (m & 65536) != 0

def isDeclaredSynchronized(m):
    return (m & 131072) != 0