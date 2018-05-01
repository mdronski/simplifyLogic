import string

VARIABLES = string.ascii_lowercase
OPERATORS = "~^&|/>"
BOOLEANS = "FT"
PRECEDENCES = {'~': 4, '^': 3, '&': 2, '|': 2, '/': 2, '>': 1}


def get_variables(expression):
    variables = [letter for letter in expression if letter in VARIABLES]
    return ''.join(list(set(variables)))


def validate(expression):
    state = True
    counter = 0

    for char in expression:
        if char == '(':
            counter += 1
        if char == ')':
            counter -= 1
        if counter < 0:
            return False
        if state:
            if char == '~':
                continue
            elif char in VARIABLES + BOOLEANS:
                state = False
            elif char in ')' + OPERATORS:
                return False
        else:
            if char in OPERATORS and char != "~":
                state = True
            elif char in '(' + VARIABLES + '~':
                return False
    if counter != 0: return False
    return not state


def divide_expression(expression, operators):
    counter = 0
    for i in range(len(expression) - 1, -1, -1):       # zmieniłem 0 na -1
        if expression[i] == ')': counter += 1
        if expression[i] == '(': counter -= 1
        if expression[i] in operators and counter == 0: return i
    return -1


def convert_to_onp(expression):
    # shunting-yard algorithm
    onp_expression = ""
    operands_stack = []

    for char in expression:
        if char in VARIABLES + BOOLEANS:
            onp_expression += char
        if char in OPERATORS:
            while operands_stack and operands_stack[-1] in OPERATORS and \
                    (PRECEDENCES[char] < PRECEDENCES[operands_stack[-1]] or
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


def substitute_variables(expression, values):
    mapped_expr = list(expression)
    variables = get_variables(expression)
    # print(variables)
    # print(values)
    var_mapped = dict(zip(variables, values))
    # print(var_mapped)
    # print(mapped_expr)
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
        return "ERROR"
    mapped_expr = substitute_variables(convert_to_onp(expression), values)
    stack = list("")
    for x in mapped_expr:
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
    result = ["",[]]
    for c1, c2 in zip(vec1[0], vec2[0]):
        if c1 == c2:
            result[0] += c1
        else:
            diff_counter += 1
            result[0] += "-"
    if diff_counter == 1:
        result[1] += (vec1[1] + vec2[1])
        return result
    else:
        return False


def parse_minterms(min_terms):
    ordered_binaries = []
    for min_term in min_terms:
        ordered_binaries.append([min_term, [int(min_term, 2)]])
    return ordered_binaries


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
        return quine_mc_cluskey(remove_duplicate_to_list(result))

    primes = []
    for p, m in (remove_duplicates(result)).items():
        primes.append([p, m])
    return primes


def convert_to_logic(expression, variables):
    main_result = ""
    for vec in expression:
        var_count = 0
        result = ""
        for i in range(len(vec[0])):
            if vec[0][i] == "-": continue
            if vec[0][i] == "0":result += "~"
            var_count += 1
            result += variables[i] + "&"
        if (var_count > 1) and len(expression) > 1:
            main_result += "(" + result[:-1] + ")|"
        else:
            main_result += result[:-1] + "|"
    return main_result[:-1]


# def replace_parenthesis(expression):
#     replaced_expression = list(expression)
#     for i in range(len(replaced_expression)):
#         if replaced_expression[i] == "(":
#             replaced_expression[i] = ")"
#         elif replaced_expression[i] == ")":
#             replaced_expression[i] = "("
#     return "".join(replaced_expression)
#
#
# def convert_to_prefix(expression):
#     reversed_expression = expression[::-1]
#     reversed_expression = replace_parenthesis(reversed_expression)
#     onp_expr = convert_to_onp(reversed_expression)
#     prefix_expr = onp_expr[::-1]
#     return prefix_expr
#
#
# def validate_reversed_prefix(expr):
#     counter = 0
#     for token in expr:
#         if token in OPERATORS :
#             if token != "~":
#                 counter -= 1
#         else:
#             counter += 1
#         if counter <= 0:
#             return False
#     return counter == 1
#

# def get_conj_expr(expression, pos):
#     end_pos = pos + 1
#     while not validate_reversed_prefix((expression[pos:end_pos])[::-1]):
#         end_pos += 1
#
#     print(expression[pos:end_pos])
#     return expression[pos:end_pos], end_pos

#
# def convert_implication(expression):
#     prefix_expression = convert_to_prefix(expression)
#     print(prefix_expression)
#     alternative_pos = prefix_expression.find("|")
#     print(alternative_pos)
#     first_expr, sec_pos = get_conj_expr(prefix_expression, alternative_pos + 1)
#     print(sec_pos)
#     second_expr, tmp = get_conj_expr(prefix_expression, sec_pos)
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


def tree_to_logic(expr, precedence):
    if type(expr) is not tuple:
        return expr
    if expr[0] == '~':
        if type(expr[1]) is tuple:
            result = '~(' + tree_to_logic(expr[1], 0) + ')'
        else:
            result = '~' + expr[1]
    else:
        result = [tree_to_logic(expression, PRECEDENCES[expr[0]]) for expression in expr[1]]
        result = expr[0].join(result)
        if precedence >= PRECEDENCES[expr[0]]:
            result = '(' + result + ')'
    return result



def make_tree(onp_expr):
    stack = []

    for char in onp_expr:

        if not char in OPERATORS:
            stack.append(char)
        else:
            if char == '~':
                expr = (char, stack.pop())
            else:
                right_expr = [stack.pop()]
                left_expr = [stack.pop()]
                expr = (char, left_expr + right_expr)
            stack.append(expr)

    expr = stack.pop()
    return expr


def find_disjunction(expr):
    if type(expr) is not tuple:
        return expr
    if expr[0] == '~':
        if expr[1][0] == '&':
            expr = ('/', expr[1][1])
    return expr


def find_implications(expr):
    if type(expr) is not tuple:
        return expr
    if expr[0] == '|':
        for i, elem1 in enumerate(expr[1]):
            for j, elem2 in enumerate(expr[1]):
                if i != j:
                    if elem1[0] == '~':
                        expr[1][i] = ('>',  [elem1[1][0], elem2])
                        del expr[1][j]
        if len(expr[1]) == 1:
            expr = expr[1][0]
    return expr


def check_negation(exp1, exp2):
    log1 = tree_to_logic(exp1, 0)
    log2 = tree_to_logic(exp2, 0)

    if len(get_variables(log1)) != len(get_variables(log2)):
        return False
    b = binary_generator(len(get_variables(log1)))

    for binary in b:
        if evaluate_logic(log1, binary) and evaluate_logic(log2, binary):
            return False

    return True


def check_if_can_be_xor(exp1, exp2):
    for i1, e1 in enumerate(exp1[1]):
        has_negation = False
        for i2, e2 in enumerate(exp2[1]):
            s1 = set(get_variables(str(e1)))
            s2 = set(get_variables(str(e2)))
            if s1 & s2 == s1 and s1 & s2 == s2:
                if check_negation(e1, e2):
                    has_negation = True
        if not has_negation:
            return False
    return True


def find_xors(expr):
    if type(expr) is not tuple:
        return expr
    if expr[0] == "|":
        exp1 = expr[1][0]
        exp2 = expr[1][1]
        if exp1[0] == "&" and exp2[0] == "&":
            if check_if_can_be_xor(exp1, exp2):
                if exp1[1][0][0] == "~":
                    expr = ('^', [exp1[1][0][1]] + [exp1[1][1]])
                else:
                    expr = ('^', [exp1[1][0]] + [exp1[1][1][1]])
    return expr


def find_shorter_substitutes(expr):
    if type(expr) is not tuple:
        return expr
    if expr[0] == '~':
        shortened_expr = (expr[0], find_shorter_substitutes(expr[1]))
    else:
        shortened_expr = (expr[0], [find_shorter_substitutes(e) for e in expr[1]])
    done = False
    while not done:
        expr = shortened_expr
        shortened_expr = find_disjunction(shortened_expr)
        shortened_expr = find_implications(shortened_expr)
        shortened_expr = find_xors(shortened_expr)
        if expr == shortened_expr:
            done = True

    return expr


#
# def get_conj_expr(expr, pos):
#     if expr[pos] != "&":
#         return [], -1
#
#     end_pos = pos
#
#     counter = 2
#     while counter > 0:
#         end_pos -= 1
#         if expr[end_pos] == "~":
#             pass
#         elif expr[end_pos] in OPERATORS:
#             counter += 1
#         else:
#             counter -= 1
#
#     end_pos -= 1
#     return expr[end_pos+1:pos], end_pos
#
#
# def get_neg_expr(expr, pos):
#     if expr[pos] != "~":
#         return [], -1
#
#     end_pos = pos
#
#     counter = 1
#     while counter > 0:
#         end_pos -= 1
#         if expr[end_pos] == "~":
#             pass
#         elif expr[end_pos] in OPERATORS:
#             counter += 1
#         else:
#             counter -= 1
#
#     end_pos -= 1
#     return expr[end_pos+1:pos], end_pos
#
#
# def convert_xor(expr):
#     onp_expr = convert_to_onp(expr)
#     print(onp_expr)
#
#     alter_pos = divide_expression(onp_expr, "|")
#
#     if alter_pos < 0:
#         return onp_expr
#
#     exp1, second_pos = get_conj_expr(onp_expr, alter_pos - 1)
#     exp2, last_pos = get_conj_expr(onp_expr, second_pos)
#     last_pos += 1
#
#     if not exp1 or not exp2:
#         return onp_expr
#
#     print(exp1)
#     print(exp2)
#
#     if exp1[-1] == "~":
#         token1, pos = get_neg_expr(exp1, len(exp1) - 1)
#         if pos == -1:
#             return onp_expr
#         token2 = exp1[:pos+1]
#
#         s = token2 + "~" + token1
#         if exp2 == s:
#             new_expr = onp_expr[:last_pos] + convert_xor(token1) + convert_xor(token2) + "^" + onp_expr[alter_pos + 1:]
#             print(new_expr)
#             return new_expr
#         else:
#             return expr
#
#     else:
#         token1, pos = get_neg_expr(exp2, len(exp2) - 1)
#         if pos == -1:
#             return onp_expr
#         token2 = exp2[:pos+1]
#
#         s = token2 + "~" + token1
#         if exp1 == s:
#             new_expr = onp_expr[:last_pos] + convert_xor(token1) + convert_xor(token2) + "^" + onp_expr[alter_pos+1:]
#             print(new_expr)
#             return new_expr
#         else:
#             return onp_expr
#
#     # print(token1)
#     # print(token2)
#
#


# def convert_implication(expression):
#     was_parenthesis = False
#     while expression[0] == '(' and expression[-1] == ')' and validate(expression[1:-1]):
#         expression = expression[1:-1]
#         was_parenthesis = True
#
#     alter_pos = divide_expression(expression, "|")
#     if alter_pos > 0:
#         first_expr = expression[:alter_pos]
#         second_expr = expression[alter_pos+1:]
#     else:
#         if was_parenthesis:
#             return "(" + expression + ")"
#         return expression
#
#     have_common_variables = set(get_variables(first_expr)) & set(get_variables(second_expr)) != set()
#     #
#     # print(first_expr)
#     # print(second_expr)
#
#     if have_common_variables:
#         if was_parenthesis:
#             return "(" + convert_implication(first_expr) + "|" + convert_implication(second_expr) + ")"
#         return convert_implication(first_expr) + "|" + convert_implication(second_expr)
#
#     if first_expr[0] != "~" and second_expr[0] == "~" and (len(second_expr) == 2 or second_expr[1] == "("):
#         if was_parenthesis:
#             return "(" + convert_implication(first_expr) + ">" + convert_implication(second_expr[1:]) + ")"
#         return convert_implication(first_expr) + ">" + convert_implication(second_expr[1:])
#
#     if first_expr[0] == "~" and second_expr[0] != "~" and (len(first_expr) == 2 or first_expr[1] == "("):
#         if was_parenthesis:
#             return "(" + convert_implication(second_expr) + ">" + convert_implication(first_expr[1:]) + ")"
#         return convert_implication(second_expr) + ">" + convert_implication(first_expr[1:])
#
#     if was_parenthesis:
#         return "(" + convert_implication(first_expr) + "|" + convert_implication(second_expr) + ")"
#     return convert_implication(first_expr) + "|" + convert_implication(second_expr)

#
#
# def convert_xor(expression):
#     was_parenthesis = False
#     while expression[0] == '(' and expression[-1] == ')' and validate(expression[1:-1]):
#         expression = expression[1:-1]
#         was_parenthesis = True
#
#     alter_pos = divide_expression(expression, "|")
#     if alter_pos > 0:
#         first_expr = expression[:alter_pos]
#         second_expr = expression[alter_pos + 1:]
#     else:
#         if was_parenthesis:
#             return "(" + expression + ")"
#         return expression
#
#     if first_expr[0] != "(" or first_expr[-1] != ")" or second_expr[0] != "(" or second_expr[-1] != ")":
#         if was_parenthesis:
#             return "(" + convert_xor(first_expr) + "|" + convert_xor(second_expr) + ")"
#         return convert_xor(first_expr) + "|" + convert_xor(second_expr)


def check(expr1, expr2):
    b = binary_generator(len(get_variables(expr1)))
    min_terms1 = [min_term for min_term in b if evaluate_logic(expr1, min_term)]

    b = binary_generator(len(get_variables(expr2)))
    min_terms2 = [min_term for min_term in b if evaluate_logic(expr2, min_term)]

    s1 = set(min_terms1)
    s2 = set(min_terms2)

    return s1 & s2 == s1 and s1 & s2 == s2


def remove_redundant_parenthesis(expr):
    for i in range(len(expr)):
        if i >= len(expr):
            break
        if expr[i] == "(":
            j = i
            counter = 1
            while counter > 0:
                j += 1
                if expr[j] == "(":
                    counter += 1
                elif expr[j] == ")":
                    counter -= 1
                else:
                    pass
            tmp_expr = expr[:i] + expr[i+1:j] + expr[j+1:]
            if check(expr, tmp_expr):
                expr = tmp_expr
    return expr


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
            min_complexity = complexity
            best_primes = primes_in_cover

    return best_primes


def calculate_complexity(primes):

    complexity = len(primes) - 1
    for prime in primes:
        tmp_complexity = 0
        for i in prime[0]:
            if i in "1": tmp_complexity += 1
            elif i == "0": tmp_complexity += 2
            elif i == "-": pass
        complexity += tmp_complexity


    return complexity


def remove_spaces(expression):
    return expression.replace(" ", "")


def check_if_tautology(min_terms, var_count):
    if len(min_terms) == 0:
        print("F")
        return True
    if len(min_terms) == 2**var_count:
        print("T")
        return True


def main(expression):
    expr1 = ""
    expr2 = ""
    expr3 = ""
    expr4 = ""
    expr5 = ""
    min_expr = ""
    try:

        expr = remove_spaces(expression)
        if not validate(expr):
            print("ERROR")
            return
        # print(expr)
        variables = get_variables(expr)
        b = binary_generator(len(variables))
        min_terms = [minTerm for minTerm in b if evaluate_logic(expr, minTerm)]

        if check_if_tautology(min_terms, len(variables)):
            return

        expr2 = tree_to_logic(find_shorter_substitutes(make_tree(convert_to_onp(expr))), 0)
        # print(expr2)

        parsed_min_terms = parse_minterms(min_terms)
        primes = quine_mc_cluskey(parsed_min_terms)

        expr3 = convert_to_logic(primes, variables)
        # print(expr3)

        optimized_primes = petrick_method_optimalization(primes, parsed_min_terms)
        expr4 = convert_to_logic(optimized_primes, variables)
        # print(expr4)

        expr5 = tree_to_logic(find_shorter_substitutes(make_tree(convert_to_onp(expr4))), 0)
        # print(expr5)


        expr_list = [expr, expr2, expr3, expr4, expr5]
        min_length = 999999
        for exp in expr_list:
            if len(exp) < min_length:
                min_expr = exp
                min_length = len(exp)

        min_expr = remove_redundant_parenthesis(min_expr)

        if check(expr, min_expr):
            print(expr + " == " + min_expr)
        else:
            print(expr + " == " + expr)

    except:

        for elem in [expr1, expr2, expr3, expr4, expr5, min_expr]:
            if elem != "":
                print(elem)
                break


expr_list = ["a<(b&c)", "(a|b)|(c|a|b)", "~(~a|~b)", "~a|~~b", "(p/q)/(p/q)", "(a&~b)|(~a&b)", "a|~a&(b|~b)|F",
             "((a|b))^d", "((a&c&d)&~(b|e))|(~(a&c&d)&(b|e))"]
for exp in expr_list:
    main(exp)

# main(expr_list[-1])
#
