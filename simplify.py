import string

VARIABLES = string.ascii_lowercase
OPERATORS = "~^&|/>"
BOOLEANS = "FT"
PRECEDENCES = {'~': 4, '^': 3, '&': 2, '|': 2, '/': 2, '>': 1}


def get_variables(expression):
    variables = [letter for letter in expression if letter in VARIABLES]
    return ''.join(list(set(variables)))


def validate(expression):
    variables = string.ascii_lowercase + 'T' + 'F'
    operators = "~^&|/>"
    state = True
    counter = 0

    for char in expression:
        if char == '(': counter += 1
        if char == ')': counter -= 1
        if counter < 0: return False
        if state:
            if char == '~': state = True
            elif char in variables: state = False
            elif char in ')' + operators: return False
        else:
            if char in operators: state = True
            elif char in '(' + variables + '~': return False
    if counter != 0: return False
    return not state


def divide_expression(expression, operators):
    counter = 0
    for i in range(len(expression) - 1, -1, -1):       # zmieniłem 0 na -1
        if expression[i] == ')': counter += 1
        if expression[i] == '(': counter -= 1
        if expression[i] in operators and counter == 0: return i
    return -1

#
# def onp(expression):
#     binary_operators = "^&|/>"
#     while expression[0] == '(' and expression[-1] == ')' and validate(expression[1:-1]):
#         expression = expression[1:-1]
#
#     for p in [result for result in [divide_expression(expression, operator) for operator in binary_operators] if result >= 0]:
#         print(onp(expression[:p]) + onp(expression[p + 1:]) + expression[p])
#         return onp(expression[:p]) + onp(expression[p + 1:]) + expression[p]
#
#     p = divide_expression(expression, '~')
#     if p >= 0:
#         print(p)
#         print(expression)
#         print(onp(expression[p + 1:]))
#         print(expression[p])
#         print(onp(expression[p:]) + expression[p])
#         return onp(expression[p + 1:]) + expression[p]
#
#     return expression


def convert_to_onp(expression):
    # shunting-yard algorithm
    onp_expression = ""
    operands_stack = []

    for char in expression:
        if char in VARIABLES + BOOLEANS:
            onp_expression += char
        if char in OPERATORS:
            while operands_stack and operands_stack[-1] in OPERATORS and \
                    (PRECEDENCES[char] < PRECEDENCES[operands_stack[-1]]  or
                     operands_stack[-1] == "~" and PRECEDENCES[operands_stack[-1]] > PRECEDENCES[char]):
                onp_expression += operands_stack.pop()
            operands_stack.append(char)
        if char == "(":
            operands_stack.append(char)
        if char == ")":
            while operands_stack[-1] != "(":
                onp_expression += operands_stack.pop()
            operands_stack.pop()
    while operands_stack:
        onp_expression += operands_stack.pop()
    return onp_expression


def substitude_variables(expression, values):
    mapped_expr = list(expression)
    variables = get_variables(expression)
    var_mapped = dict(zip(variables, values))
    for i in range(len(mapped_expr)):
        if mapped_expr[i] in VARIABLES:
            mapped_expr[i] = var_mapped[mapped_expr[i]]
        elif mapped_expr[i] == "T":
            mapped_expr[i] = "1"
        elif mapped_expr[i] == "F":
            mapped_expr[i] = "0"
    return ''.join(mapped_expr)


def evaluate_logic(expression, values):
    if not validate(expression):
        print("ERROR")
        return False
    mappedExpr = substitude_variables(convert_to_onp(expression), values)
    stack = list("")
    for x in mappedExpr:
        if x in '01': stack.append(int(x))
        else:
            y1 = not not stack.pop()
            if x == '~':
                stack.append(not y1)
            elif x == "T": stack.append(True)
            elif x == "F": stack.append(False)
            else:
                y2 = not not stack.pop()
                if x == '&': stack.append(y1 and y2)
                elif x == '|': stack.append(y1 or y2)
                elif x == '>': stack.append(y1 or (not y2))
                elif x == '/': stack.append(not (y1 and y2))
                elif x == '^': stack.append((y1 and not y2) or (not y1 and y2))
    return stack.pop()


def binary_generator(n):
    if n == 0: yield ""
    else:
        for c in binary_generator(n - 1):
            yield "0" + c
            yield "1" + c


def latch(vec1, vec2):
    diff_counter = 0
    result = ["",[]]  #change
    for c1, c2 in zip(vec1[0], vec2[0]): #change
        if c1 == c2:
            result[0] += c1 #change
        else:
            diff_counter += 1
            result[0] += "-"  #change
    if diff_counter == 1:
        result[1] += (vec1[1] + vec2[1]) #change
        return result
    else:
        return False


def parse_minterms(binaries):
    ordered_binaries = []
    for binary in binaries:
        ordered_binaries.append([binary, [int(binary, 2)]])
    return ordered_binaries


def read_data(file_name):
    data = open(file_name, "r")
    result = set(data.read().splitlines())
    data.close()
    return result


def remove_duplicates(primes):
    clean_primes = {}
    for prime in primes:
        clean_primes[prime[0]] = prime[1]
    return clean_primes


def remove_duplicate_to_list(primes):
    primes_set = remove_duplicates(primes)
    new_primes = []
    for key, value in primes_set.items():
        new_primes.append([key, value])
    return new_primes


def quine_mc_cluskey(binaries):
    any_latch = False
    result = []
    for binary1 in binaries:
        founded_latch = False
        for binary2 in binaries:
            vec = latch(binary1, binary2)
            if vec:
                result.append(vec)
                founded_latch = any_latch = True
        if not founded_latch: result.append(binary1)
    if any_latch:
        #print(result)
        return quine_mc_cluskey(remove_duplicate_to_list(result))

    primes = []
    for p, m in (remove_duplicates(result)).items():
        primes.append([p, m])
    return primes


def convert_to_logic(expression):
    main_result = ""
    for vec in expression:
        var_count = 0
        result = ""
        for elem in range(len(vec[0])):
            if vec[0][elem] == "-": continue
            if vec[0][elem] == "0":result += "~"
            var_count += 1
            result += string.ascii_lowercase[elem]+"&"
        if (var_count > 1) and len(expression) > 1:
            main_result += "(" + result[:-1] + ")|"
        else:
            main_result += result[:-1] + "|"
    return main_result[:-1]


def replace_parenthesis(expression):
    replaced_expression = list(expression)
    for i in range(len(replaced_expression)):
        if replaced_expression[i] == "(":
            replaced_expression[i] = ")"
        elif replaced_expression[i] == ")":
            replaced_expression[i] = "("
    return "".join(replaced_expression)


def convert_to_prefix(expression):
    reversed_expression = expression[::-1]
    reversed_expression = replace_parenthesis(reversed_expression)
    onp_expr = convert_to_onp(reversed_expression)
    prefix_expr = onp_expr[::-1]
    return prefix_expr


def validate_reversed_prefix(expr):
    counter = 0
    for token in expr:
        if token in OPERATORS :
            if token != "~":
                counter -= 1
        else:
            counter += 1
        if counter <= 0:
            return False
    return counter == 1


def get_partial_expr(expression, pos):
    end_pos = pos + 1
    while not validate_reversed_prefix((expression[pos:end_pos])[::-1]):
        end_pos += 1

    print(expression[pos:end_pos])
    return expression[pos:end_pos], end_pos

#
# def convert_implication(expression):
#     prefix_expression = convert_to_prefix(expression)
#     print(prefix_expression)
#     alternative_pos = prefix_expression.find("|")
#     print(alternative_pos)
#     first_expr, sec_pos = get_partial_expr(prefix_expression, alternative_pos + 1)
#     print(sec_pos)
#     second_expr, tmp = get_partial_expr(prefix_expression, sec_pos)
#
#     print(first_expr)
#     print(second_expr)
#
#     have_common_variables = set(get_variables(first_expr)) & set(get_variables(second_expr)) != set()
#     was_converted = False
#     if not have_common_variables and first_expr[0] == "~" and second_expr[0] != "~":
#         expr_list = list(prefix_expression)
#         expr_list[alternative_pos] = expr_list[alternative_pos + 1] = ""
#         expr_list[alternative_pos] = ">"
#         was_converted = True
#
#     if not have_common_variables and first_expr[0] != "~" and second_expr[0] == "~":
#         expr_list = []
#         expr_list.append(">")
#         expr_list.append(second_expr[1:])
#         expr_list.append(first_expr)
#         was_converted = True
#
#     print("".join(expr_list))
#     return "".join(expr_list), was_converted


def convert_implication2(expression):
    was_parenthesis = False
    while expression[0] == '(' and expression[-1] == ')' and validate(expression[1:-1]):
        expression = expression[1:-1]
        was_parenthesis = True

    alter_pos = divide_expression(expression, "|")
    if alter_pos > 0:
        first_expr = expression[:alter_pos]
        second_expr = expression[alter_pos+1:]
    else:
        if was_parenthesis:
            return "(" + expression + ")"
        return expression

    have_common_variables = set(get_variables(first_expr)) & set(get_variables(second_expr)) != set()

    if have_common_variables:
        if was_parenthesis:
            return "(" + convert_implication2(first_expr) + "|" + convert_implication2(second_expr) + ")"
        return convert_implication2(first_expr) + "|" + convert_implication2(second_expr)

    print(first_expr)
    print(second_expr)

    if first_expr[0] != "~" and second_expr[0] == "~" and (len(second_expr) == 1 or second_expr[1] == "("):
        if was_parenthesis:
            return "(" + convert_implication2(first_expr) + ">" + convert_implication2(second_expr[1:]) + ")"
        return convert_implication2(first_expr) + ">" + convert_implication2(second_expr[1:])

    if first_expr[0] == "~" and second_expr[0] != "~" and (len(first_expr) == 1 or first_expr[1] == "("):
        if was_parenthesis:
            return "(" + convert_implication2(second_expr) + ">" + convert_implication2(first_expr[1:]) + ")"
        return convert_implication2(second_expr) + ">" + convert_implication2(first_expr[1:])

    if was_parenthesis:
        return "(" + convert_implication2(first_expr) + "|" + convert_implication2(second_expr) + ")"
    return convert_implication2(first_expr) + "|" + convert_implication2(second_expr)


def check(expr, binaries):
    for result in [evaluate_logic(expr, binary) for binary in binaries]: print(result)


def petrick_method_optimalization(primes, min_terms):

    chart = []
    for min_term in min_terms:
        column = []
        for i in range(len(primes)):
            if min_term[1][0] in primes[i][1]:
                column.append(i)
        chart.append(column)

    covers = []
    if len(chart) > 0:
        covers = [{i} for i in chart[0]]
    for i in range(1, len(chart)):
        new_covers = []
        for cover in covers:
            for prime_index in chart[i]:
                x = set(cover)
                x.add(prime_index)
                append = True
                for j in range(len(new_covers) - 1, -1, -1):
                    if x <= new_covers[j]:
                        del new_covers[j]
                    elif x > new_covers[j]:
                        append = False
                if append:
                    new_covers.append(x)
        covers = new_covers

    min_complexity = 99999999
    for cover in covers:
        primes_in_cover = [primes[prime_index] for prime_index in cover]
        complexity = calculate_complexity(primes_in_cover)
        if complexity < min_complexity:
            # print(primes_in_cover)
            # print(complexity)
            min_complexity = complexity
            best_primes = primes_in_cover

    return best_primes


def calculate_complexity(primes):

    complexity = len(primes) - 1
    for prime in primes:
        tmp_complexity = 0
        was_xnor = False
        for i in prime[0]:
            if i in "1^": tmp_complexity += 1
            elif i == "0": tmp_complexity += 2
            elif i == "-": pass
            elif i == "~":
                if not was_xnor:
                    tmp_complexity += 4
                    was_xnor = True
                else:
                    tmp_complexity += 1
        complexity += tmp_complexity
    #
    # print(primes)
    # print(complexity)

    return complexity


def remove_spaces(expression):
    return expression.replace(" ", "")


def main():
    binaries = read_data("data.txt")
    binaries = {"000", "001", "010", "101", "110", "111"}
    # print(binaries)
    parsed_binaries = parse_minterms(binaries)
    print()
    result = quine_mc_cluskey(parsed_binaries)
    # print(result)
    print()
    expr = convert_to_logic(result)

    r = [['~-~', [2, 0, 5, 7]], ['00-', [0, 1]], ['1-1', [5, 7]], ['-01', [1, 5]], ['11-', [6, 7]], ['0-0', [2, 0]],
         ['~~-', [0, 1, 6, 7]], ['-^^', [2, 6, 1, 5]], ['-10', [2, 6]]]
    print(r)
    x = petrick_method_optimalization(r, parsed_binaries)
    print(x)


def check_if_boolean(min_terms, var_count):
    if len(min_terms) == 0:
        print("F")
        return True
    if len(min_terms) == var_count**2:
        print("T")
        return True

def minimize(expression):
    # temporary input of expression
    expr_raw = "(a^c)|~(b&d)"
    expr = remove_spaces(expression)
    if not validate(expr):
        print("ERROR")
        return
    print(expr)
    variables = get_variables(expr)
    b = binary_generator(len(variables))
    min_terms = [minTerm for minTerm in b if evaluate_logic(expr, minTerm)]
#    print(min_terms)
    if check_if_boolean(min_terms, len(variables)):
        return
    parsed_min_terms = parse_minterms(min_terms)
    primes = quine_mc_cluskey(parsed_min_terms)
    print(primes)
    print(convert_to_logic(primes))
    optimized_primes = petrick_method_optimalization(primes, parsed_min_terms)
    print(optimized_primes)
    expr = convert_to_logic(optimized_primes)
    print(expr)
    return expr


# convert_implication("(a^c)|~(b&d)")

# print("~(a^c)|(b|~d&c)")
# print(convert_implication2("~(a^c)|(b|~(d&c))"))
x = minimize("(~(a&c)|(b|~(d&c)))/(e&f/(a&c)|b&d)")
print(convert_implication2(x))
