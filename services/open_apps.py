from AppOpener import open, close
    

def AppOpen(query: str):
    open(query, match_closest=True)
    
    return f'Opening {query}'
    
def AppClose(query: str):
    close(query, match_closest=True)
    return f'Closing {query}'