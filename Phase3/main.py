def convert_pda_to_cfg(pda_states, pda_alphabets, stack_alphabets, pda_final_states, pda_transitions):
    non_transitions, transitions = list(), list()

    for transition in pda_transitions:
        transition = transition.split(',')
        if transition[3] == "":
            non_transitions.append(transition)
        else:
            transitions.append(transition)

    cfg = list()
    for i in range(len(pda_states)):
        if i != 0:
            for transition in transitions:
                production = ''
                production = production + str(transition[0]) + str(transition[2]) + 'qf'
                cfg.append(production)

                for j in range(len(pda_states) - 1):
                    production = ''
                    production = production.join(transition[1])
                    cfg.append(production)

                    for k in range(len(pda_states)):
                        production = ''
                        if len(transition[3]) <= 1:
                            production = production.join(
                                str('(' + transition[0] + str(transition[3][0]) + 'q' + str(k) + ')'))
                        else:
                            production = production.join(
                                str('(' + transition[0] + str(transition[3][0]) + 'q' + str(k) + ')' + '(' + 'q' + str(
                                    k) + str(transition[3][1]) + 'qf' + ')'))

                        cfg.append(production)
        else:
            for transition in transitions:
                production = ''
                production = production + str(transition[0]) + str(transition[2]) + str(transition[4])
                cfg.append(production)

                for j in range(len(pda_states) - 1):
                    production = ''
                    production = production.join(transition[1])
                    cfg.append(production)

                    for k in range(len(pda_states)):
                        production = ''
                        if len(transition[3]) <= 1:
                            production = production.join(
                                str('(' + transition[0] + str(transition[3][0]) + 'q' + str(k) + ')'))
                        else:
                            production = production.join(
                                str('(' + transition[0] + str(transition[3][0]) + 'q' + str(k) + ')' + '(' + 'q' + str(
                                    k) + str(transition[3][1]) +
                                    transition[4] + ')'))

                        cfg.append(production)

    unit_productions = list()
    for transition in non_transitions:
        production = ''
        production = production + str(transition[0]) + str(transition[2]) + str(transition[4]) + ' -> '

        if transition[1] == '':
            production = production + '#'
        else:
            production = production + str(transition[1])

        unit_productions.append(production)

    for unit_production in unit_productions:
        cfg.append(unit_production)

    return cfg


def input_pda():
    pda_states = input().strip('{}').split(',')
    pda_alphabets = input().strip('{}').split(',')
    stack_alphabets = input().strip('{}').split(',')
    pda_final_states = input().strip('{}').split(',')
    n = int(input())
    input_transitions = []
    for _ in range(n):
        input_transitions.append(list(input().strip().strip('()').replace('(', '').replace(')', '').split(',')))

    pda_transitions = [','.join(transition) for transition in input_transitions]
    pda_transitions = [transition.replace('#', '') for transition in pda_transitions]

    return [pda_states, pda_alphabets, stack_alphabets, pda_final_states, pda_transitions]


def print_grammar(cfg, pda_states):
    for i in range(4 * len(pda_states)):
        print(cfg[0] + ' -> ' + cfg[1] + cfg[2] + ' | ' + cfg[1] + cfg[3])

        for j in range(2 * len(pda_states)):
            del cfg[0]

    for i in range(len(cfg)):
        print(cfg[i])


if __name__ == "__main__":
    states, alphabets, stack_contents, final_states, transitions = input_pda()
    grammar = convert_pda_to_cfg(states, alphabets, stack_contents, final_states, transitions)
    print_grammar(grammar, states)
