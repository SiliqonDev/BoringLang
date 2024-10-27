### POSITION

class Position:
    def __init__(self, index, ln, col, filename, filetext):
        self.index = index
        self.ln = ln
        self.col = col
        self.filename = filename
        self.filetext = filetext
    
    def next(self, current_char=None):
        self.index += 1
        self.col += 1

        if current_char == "\n":
            self.ln += 1
            self.col = 0
        
        return self
    
    def previous(self, current_char=None):
        self.index -= 1
        self.col -= 1

        return self
    
    def copy(self):
        return Position(self.index, self.ln, self.col, self.filename, self.filetext)