class NPDA:
    def __init__(self, states, pda_alphabets, stack_alphabets, final_states, transitions):
        self.states = states
        self.pda_alphabets = pda_alphabets
        self.stack_alphabets = stack_alphabets
        self.final_states = final_states
        self.transitions = transitions
    
    def check_condition(self,input_string):
        input_string = input_string.replace("#","")
        if len(self.states) == 1:
            if len(input_string) == len(self.transitions):
                return True
            elif len(input_string) > len(self.transitions):
                return False
        return True

    def accept_string(self, input_string):
        stack = ['$']
        current_state = self.states[0]

        for symbol in input_string:
            valid_transition = False
            for transition in self.transitions:
                if transition[0] == current_state and transition[1] == symbol and transition[2] == stack[-1]:
                    stack.pop()
                    if transition[3] != '#':
                        stack.extend(list(transition[3]))
                    current_state = transition[4]
                    valid_transition = True
                    break
            for transition in self.transitions:
                if transition[0] == current_state and transition[1] == symbol and transition[2] == '#' and valid_transition == False:
                    if transition[3] != '#':
                        stack.extend(list(transition[3]))
                    current_state = transition[4]
                    valid_transition = True
                    break
                elif transition[0] == current_state and transition[1] == symbol and transition[2] != stack[-1] and valid_transition == False:
                    return False
            
            if current_state in self.final_states:
                if len(self.states) != 1 :
                    return True
                if self.check_condition(input_string):
                    return True
                else:
                    return False


        
        if current_state in self.final_states :
            return True
        else:
            return False

# Parse the input and create the NPDA
input_states = input().strip('{}').split(',')
input_pda_alphabets = input().strip('{}').split(',')
input_stack_alphabets = input().strip('{}').split(',')
input_final_states = input().strip('{}').split(',')
num_transitions = int(input())
input_transitions = []
for _ in range(num_transitions):
    input_transitions.append(tuple(input().strip().strip('()').replace('(', '').replace(')', '').split(',')))
input_string = input()




for transition in input_transitions:
    if transition[1] == '#' and transition[2]== '#' and transition[3] == '#':
        # position = int( len(input_string)/2);
        # input_string = input_string[:position] + "#" + input_string[position:]
        dest = transition[0] ## q0
        source = transition[4] ##q1
        for i in range(num_transitions):
            if input_transitions[i][0] == source:
                input_transitions[i] =  (dest, input_transitions[i][1], input_transitions[i][2], input_transitions[i][3], input_transitions[i][4])
            if input_transitions[i][4] == source:
                input_transitions[i] =  (input_transitions[i][0], input_transitions[i][1], input_transitions[i][2], input_transitions[i][3], dest)

input_string = input_string + '#'


npda = NPDA(input_states, input_pda_alphabets, input_stack_alphabets, input_final_states, input_transitions)


if npda.accept_string(input_string):
    print("Accepted")
else:
    print("Rejected")

