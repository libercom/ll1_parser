import string

# Check whether the first symbol of a first or follow set is a non-terminal symbol.
def check_first_follow(first_follow, non_terminals):
  for key in first_follow:
    for value in first_follow[key]:
      if value[0] in non_terminals:
        return True

class LL1:
    def __init__(self, file):
        with open(file) as f:
            input = f.read().split('\n')
        
        self.non_terminals = []
        self.terminals = []
        self.start = 'S'
        self.available_symbols = list(string.ascii_uppercase)
        self.new_value = False
        self.grammar = {}

        for line in input:
            self.non_terminals.append(line[0])
            
            for terminal in line[2:]:
                if (terminal.islower()):
                    self.terminals.append(terminal)
            
            if line[0] not in self.grammar:
                self.grammar[line[0]] = []
            
            self.grammar[line[0]].append(line[2:])
        
        self.non_terminals = list(set(self.non_terminals))
        self.terminals = list(set(self.terminals))

        for char in self.non_terminals:
            if char in self.available_symbols:
                self.available_symbols.remove(char)

    def compute_first(self):
        # Initialize the first dictionary
        self.first = {}

        for key in self.non_terminals:
          self.first[key] = []

        # If the first character of a production is a terminal symbol, add that symbol to the \first\ dictionary. Otherwise, add the entire production to the \first\ dictionary.
        for key in self.grammar:
            for value in self.grammar[key]:
                if (value[0] in self.terminals):
                    self.first[key].append(value[0])
                else:
                    self.first[key].append(value)
                    self.first[key] = list(set(self.first[key]))
        
        # Compute the first set until there are no more non-terminal symbols in the first dictionary.
        while (check_first_follow(self.first, self.non_terminals)):
          for key in self.first:
            tab = []
            for value in self.first[key]:
              # If a value of first(key) is a non-terminal symbol and first(x) (where x is that non-terminal) contains epsilon, we will replace that value with first(x).
              if (value[0] in self.non_terminals) and ('_' in self.first[value[0]]) and (len(value) > 1):
                tab.extend(self.first[value[0]])
                tab.remove('_')
                tab.append(value[1:])
              # If a value of first(key) is a non-terminal symbol, replace it with the values of first(x) (where x is that non-terminal).
              elif (value[0] in self.non_terminals):
                tab.extend(self.first[value[0]])
              # If none of the cases matches we leave it as it is
              else:
                tab.append(value)

            tab = list(set(tab))
            self.first[key] = tab
      
    def compute_follow(self):
        # Initialize the follow dictionary
        self.follow = {}
        for key in self.non_terminals:
          self.follow[key] = []
        
        # By default \S\ contains \$\
        self.follow['S'].append('$')

        for key in self.grammar:
          for value in self.grammar[key]:
            for i in range(0, len(value)):
              if value[i] in self.non_terminals:
                # If we are at the last character of the production we will push the key because the non-terminal is not followed by any terminals
                if i == len(value) - 1:
                  self.follow[value[i]].append(key)
                # If the non-terminal is followed by a terminal we push the terminal
                elif value[i + 1] in self.terminals:
                  self.follow[value[i]].append(value[i + 1])
                # If none of the above matches we push the first terminal of the next non-terminal
                else:
                  tab = self.first[value[i + 1]]
                  if '_' in tab:
                    tab.remove('_')
                    tab.append(key)
                  self.follow[value[i]].extend(tab)
        
        while (check_first_follow(self.follow, self.non_terminals)):
          for key in self.follow:
            tab = []
            for value in self.follow[key]:
              # If it's a non-terminal symbol, push the follow of that non-terminal to it.
              if (value in self.non_terminals) and (key not in self.follow[value]):
                tab.extend(self.follow[value])
              # If it's a terminal we leave it as it is
              elif value in self.terminals or value == '$':
                tab.append(value)

            tab = list(set(tab))
            self.follow[key] = tab

    def compute_parsing_table(self):
        # Initialize the column values (terminals), for example: (a -> 0, b -> 1, c -> 2, etc.).
        self.column = {}
        i = 0
        for key in self.terminals:
          self.column[key] = i
          i += 1
        self.column['$'] = i

        # Initialize the row values (for each non-terminal, there will correspond an array of /n/ strings, where n is the number of terminals).
        # When we access a cell in the parsing table, we will do that by row[non_terminal_index][terminal_index], where terminal_index is from the column property.
        self.rows = {}
        for key in self.non_terminals:
          self.rows[key] = [''] * (len(self.terminals) + 1)

        # We are working with the \key\ row
        for key in self.grammar:
          for value in self.grammar[key]:
            # Columns where we will insert the production
            a = []
            # Columns where will insert a production ending in a epsilon
            b = []
            # If a production starts with a terminal, add it under the column of that terminal.
            if value[0] in self.terminals:
              a.append(value[0])
            # If a production starts with a non-terminal, add it under the columns of the terminals from the first set of that corresponding non-terminal.
            elif value[0] in self.non_terminals:
              a.extend(self.first[value[0]])
              if '_' in a:
                a.remove('_')
                b.extend(self.follow[key])
            # If the production is epsilon, we have to fill with epsilon the columns of the terminals from the follow set of the non-terminal on the left-hand side of the production.
            elif value == '_':
              b.extend(self.follow[key])

            for term in b:
              self.rows[key][self.column[term]] = '_'
            for term in a:
              self.rows[key][self.column[term]] = value

    def parse_input(self, word):
        stack = 'S$'
        input = word + '$'
        finished = False
        
        while(not finished):
          print(stack + ' | ', input  + ' | ', end=' ')

          finished, stack, input, action = self.act(stack, input)
          print(action)
        print()

        if stack == '$' and input == stack:
          print('Valid token')
        else:
          print('Invalid token!')


    def act(self, stack, input):
        if stack == '$':
          return True, stack, input, 'Done!'
        
        if stack[0] == input[0]:
          return False, stack[1:], input[1:], '-'
        
        new = self.rows[stack[0]][self.column[input[0]]]

        if new == '':
          return True, '', '', ''
        
        if new == '_':
          return False, stack[1:], input, 'ε'
        elif new != '_':
           return False, new + stack[1:], input, new
        
    def parse(self,word):
        self.compute_first()
        self.compute_follow()
        self.compute_parsing_table()
        self.parse_input(word)

a = LL1('grammar.txt')
a.parse('a')
