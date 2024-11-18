from string_with_arrows import *

### ERRORS

class Error:
    def __init__(self, pos_start, pos_end, error_name, info):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.info = info
    
    def as_string(self):
        result = f"{self.error_name}: {self.info}"
        result += f"\nFile {self.pos_start.filename}: line {self.pos_start.ln + 1}, col {self.pos_start.col}"
        result += '\n\n' + string_with_arrows(self.pos_start.filetext, self.pos_start, self.pos_end)
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, info):
        super().__init__(pos_start, pos_end, "Illegal Character", info)

class ExpectedCharError(Error):
    def __init__(self, pos_start, pos_end, info):
        super().__init__(pos_start, pos_end, "Expected Character", info)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, info):
        super().__init__(pos_start, pos_end, "Invalid Syntax", info)

class RuntimeError(Error):
    def __init__(self, pos_start, pos_end, info, context):
        super().__init__(pos_start, pos_end, "Runtime Error", info)
        self.context = context
    
    def as_string(self):
        result = self.generate_traceback()
        result += f"{self.error_name}: {self.info}"
        result += '\n\n' + string_with_arrows(self.pos_start.filetext, self.pos_start, self.pos_end)
        return result
    
    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        context = self.context

        while context:
            result = f'    File {pos.filename}, line {pos.ln + 1}, in {context.display_name}\n' + result
            pos = context.parent_entry_pos
            context = context.parent
        
        return "Traceback (most recent call last):\n" + result