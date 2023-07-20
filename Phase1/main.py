import re
from itertools import permutations

variable_idx = 0


def eliminate_non_reachables(cfg, variables):
    reachable_vars = [variables[0]]
    i = 0
    while i < len(reachable_vars):
        variable = reachable_vars[i]
        if variable in cfg:
            for transition in cfg[variable]:
                pattern = r'<\w>'
                found_vars = re.findall(pattern, transition)
                for found_var in found_vars:
                    if found_var not in reachable_vars:
                        reachable_vars.append(found_var)
        i += 1

    for variable in variables:
        if variable not in reachable_vars:
            variables.remove(variable)
            del cfg[variable]


def find_useful_vars(cfg, variables):
    useful_variable = list()
    flag = True

    for _ in range(len(variables)):
        if not flag:
            break

        flag = False
        for variable in variables:
            for transition in cfg[variable]:
                is_useful_variable = True
                pattern = r'<\w>'
                found_vars = re.findall(pattern, transition)
                for found_var in found_vars:
                    if found_var not in useful_variable:
                        is_useful_variable = False
                if is_useful_variable and variable not in useful_variable:
                    flag = True
                    useful_variable.append(variable)

    return useful_variable


def removing_useless_prods(cfg, variables):
    useful_variables = find_useful_vars(cfg, variables)
    for variable in variables:
        if variable in useful_variables:
            for transition in cfg[variable]:
                pattern = r'<\w>'
                found_vars = re.findall(pattern, transition)
                for found_var in found_vars:
                    if found_var not in useful_variables:
                        cfg[variable].remove(transition)
                        break
        else:
            variables.remove(variable)
            del cfg[variable]

    eliminate_non_reachables(cfg, variables)


def introduce_intermediate_vars(prod_to_cnf, cfg, variables):
    pattern = r'<[\w,\W]>'
    found_vars = re.findall(pattern, prod_to_cnf[1])

    if len(found_vars) == 2:
        return

    transition = "".join(found_vars[1:])
    variable = next((state for state in variables if transition in cfg[state]), False)

    new_variable = variable
    global variable_idx
    if variable is False:
        new_variable = "<" + "V" + str(variable_idx) + ">"

    cfg[prod_to_cnf[0]].append(found_vars[0] + new_variable)
    cfg[prod_to_cnf[0]].remove(prod_to_cnf[1])
    if new_variable not in variables:
        variable_idx += 1
        variables.append(new_variable)
        cfg[new_variable] = [transition]

    introduce_intermediate_vars([new_variable, transition], cfg, variables)


def prod_with_multiple_vars(cfg, variables):
    for variable in variables:
        for transition in cfg[variable]:
            pattern = r'<[\w,\W]>'
            found_vars = re.findall(pattern, transition)
            if len(found_vars) > 2:
                return [variable, transition]

    return False


def find_terminals(transition):
    pattern = r'<[\w,\W]>'
    terminals = list(set(re.split(pattern, transition)))
    if "" in terminals:
        terminals.remove("")

    return terminals


def convert_terminals_to_vars(prod_to_cnf, cfg, variables):
    terminals = find_terminals(prod_to_cnf[1])

    for terminal in terminals:
        prod_form = "<" + terminal + ">"
        if prod_form not in cfg:
            variables.append(prod_form)
            cfg[prod_form] = [terminal]

    converted_prod = ""
    i = 0
    while i != len(prod_to_cnf[1]):
        if prod_to_cnf[1][i] != "<":
            converted_prod += "<" + prod_to_cnf[1][i] + ">"
        else:
            converted_prod += "<" + prod_to_cnf[1][i + 1] + ">"
            i += 2

        i += 1

    cfg[prod_to_cnf[0]][cfg[prod_to_cnf[0]].index(prod_to_cnf[1])] = converted_prod


def prod_not_in_cnf(cfg, variables):
    for variable in variables:
        for transition in cfg[variable]:
            if len(transition) > 1 and len(find_terminals(transition)) > 0:
                return variable, transition

    return False


def find_nullable_prods(cfg, variables):
    for variable in variables:
        for transition in cfg[variable]:
            if transition == "#":
                return variable

    return False


def remove_nullable_prod_from_cfg(cfg, variables, nullable_prod):
    for variable in variables:
        cfg[variable] = list(set(cfg[variable]))
        for transition in cfg[variable]:
            if nullable_prod in transition:
                prod = [nullable_prod, ""]
                calculate_all_combinations(cfg, prod, variable, transition)

        cfg[variable] = list(set(cfg[variable]))

    cfg[nullable_prod].remove("#")


def eliminate_nullable_prods(cfg, variables, nullable_prod):
    while nullable_prod is not False:
        remove_nullable_prod_from_cfg(cfg, variables, nullable_prod)
        for variable in variables:
            if variable in cfg[variable]:
                cfg[variable].remove(variable)

        nullable_prod = find_nullable_prods(cfg, variables)


def find_unit_prods(cfg, variables):
    for variable in variables:
        for transition in cfg[variable]:
            if len(transition) == 3 and transition[0] == "<":
                return variable, transition

    return False


def substitute_unit_prod(cfg, unit_prod):
    temp_transitions = cfg[unit_prod[1]]
    for transition in temp_transitions:
        cfg[unit_prod[0]].append(transition)

    cfg[unit_prod[0]].remove(unit_prod[1])


def find_available_combinations(iterable, replace_count):
    iterable = tuple(iterable)
    for indices in permutations(range(len(iterable)), replace_count):
        if list(indices) == sorted(indices):
            yield tuple(iterable[index] for index in indices)


def calculate_all_combinations(cfg, prod, variable, transition):
    replaced_var = prod[1]
    replacement_var = prod[0]
    replace_counts = transition.count(replacement_var)

    replace_indices = list()
    for start_idx in range(len(transition)):
        start_idx = transition.find(replacement_var, start_idx)
        if start_idx == -1:
            break
        replace_indices.append(start_idx)
        start_idx += len(replacement_var)

    all_combinations = list(transition)
    for i in range(1, replace_counts + 1):
        available_combinations = find_available_combinations(replace_indices, i)
        for combination in available_combinations:
            for j in combination:
                if replaced_var != "":
                    all_combinations[j + 1] = replaced_var[1]
                else:
                    all_combinations[j] = ""
                    all_combinations[j + 1] = ""
                    all_combinations[j + 2] = ""

            cfg[variable].append("".join(all_combinations))
            all_combinations = list(transition)


def remove_unit_prod_from_cfg(cfg, unit_prod, variables):
    if unit_prod[0] == variables[0]:
        substitute_unit_prod(cfg, unit_prod)
        cfg[unit_prod[0]] = list(set(cfg[unit_prod[0]]))
        return

    for variable in variables:
        cfg[variable] = list(set(cfg[variable]))
        for idx, transition in enumerate(cfg[variable]):
            if len(cfg[variable]) != idx and unit_prod[0] in transition:
                calculate_all_combinations(cfg, unit_prod, variable, transition)

        cfg[variable] = list(set(cfg[variable]))

    cfg[unit_prod[0]].remove(unit_prod[1])


def eliminate_unit_prods(cfg, variables, unit_prod):
    while unit_prod:
        remove_unit_prod_from_cfg(cfg, unit_prod, variables)
        for variable in variables:
            if variable in cfg[variable]:
                cfg[variable].remove(variable)

        unit_prod = find_unit_prods(cfg, variables)


def simplify_cfg(cfg, variables):
    nullable_prods = find_nullable_prods(cfg, variables)
    unit_prods = find_unit_prods(cfg, variables)

    while nullable_prods is not False or unit_prods is not False:
        eliminate_nullable_prods(cfg, variables, nullable_prods)
        eliminate_unit_prods(cfg, variables, unit_prods)

        nullable_prods = find_nullable_prods(cfg, variables)
        unit_prods = find_unit_prods(cfg, variables)


def conversion_to_cnf(cfg, variables):
    simplify_cfg(cfg, variables)

    prod_to_cnf = prod_not_in_cnf(cfg, variables)
    while prod_to_cnf:
        convert_terminals_to_vars(prod_to_cnf, cfg, variables)
        prod_to_cnf = prod_not_in_cnf(cfg, variables)

    prod_to_cnf = prod_with_multiple_vars(cfg, variables)
    while prod_to_cnf is not False:
        introduce_intermediate_vars(prod_to_cnf, cfg, variables)
        prod_to_cnf = prod_with_multiple_vars(cfg, variables)

    return cfg


def string_acceptance_check(cfg, input_str, variables):
    dp = [[[] for _ in range(len(input_str))] for _ in range(len(input_str))]
    for i in range(len(input_str)):
        for variable in variables:
            if input_str[i] in cfg[variable]:
                dp[i][i].append(variable)

    for i in range(2, len(input_str) + 1):
        for j in range(len(input_str) - i + 1):
            k = j + i - 1
            for l in range(j, k):
                for variable in variables:
                    is_var_derived = [False]
                    for transition in cfg[variable]:
                        pattern = r'<[^>]+>'
                        found_vars = re.findall(pattern, transition)
                        if len(found_vars) == 2 and found_vars[0] in dp[j][l] and found_vars[1] in dp[l + 1][k]:
                            is_var_derived[0] = True

                    if is_var_derived[0]:
                        dp[j][k].append(variable)

    if variables[0] in dp[0][len(input_str) - 1]:
        return True

    return False


if __name__ == '__main__':
    cfg_object = {}
    variables = list()

    n = int(input())
    for i in range(n):
        productions_line = input().split(" -> ")
        variables.append(productions_line[0])
        prod_transitions = productions_line[1].split(" | ")
        cfg_object[productions_line[0]] = prod_transitions

    input_string = input()
    start_variable = variables[0]

    removing_useless_prods(cfg_object, variables)

    conversion_to_cnf(cfg_object, variables)

    is_accepted = string_acceptance_check(cfg_object, input_string, variables)
    if is_accepted:
        print("Accepted")
    else:
        print("Rejected")
