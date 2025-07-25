from cmu_graphics import * 
def onAppStart(app):
    app.counter = 0

def onAppStart(app):
    app.counter = 0

def onKeyHold(app, keys, modifiers):
    app.counter += 1
    print(app.counter%1000, keys, modifiers)

def onKeyRelease(app, key):
    print(key)

runApp()
