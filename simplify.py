import string


def gev_variables(expression):
    variables = [letter for letter in expression if letter.isalpha()]
    return ''.join(sorted(set(variables)))


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


def onp(expression):
    operators = "~^&|/>"
    while expression[0] == '(' and expression[-1] == ')' and validate(expression[1:-1]):
        expression = expression[1:-1]

    for p in [result for result in [divide_expression(expression, operator) for operator in operators] if result >= 0]:
        return onp(expression[:p]) + onp(expression[p + 1:]) + expression[p]

    p = divide_expression(expression, '~')
    if p >= 0:
        return onp(expression[p + 1:]) + expression[p]

    return expression


def substitude(expression, variables, values):
    mapped_expr = list(expression)
    for i in range(len(expression)):
        pos = variables.find(expression[i])
        if pos >= 0: mapped_expr[i] = values[pos]
    return ''.join(mapped_expr)


def evaluate_logic(expression, values):
    if not validate(expression):
        print("ERROR")
        return False
    variables = gev_variables(expression)
    #print(variables)
    mappedExpr = substitude(onp(expression), variables, values)
    #print(mappedExpr)
    stack = list("")
    for x in mappedExpr:
        if x in '01': stack.append(int(x))
        else:
            y1 = not not stack.pop()
            if x == '~':
                stack.append(not y1)
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
    orderedBinaries = []
    for binary in binaries:
        orderedBinaries.append([binary, [int(binary, 2)]])
    return orderedBinaries


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
    if any_latch: return quine_mc_cluskey(result)

    primes = []
    for p, m in (remove_duplicates(result)).items():
        primes.append([p, m])
    return primes


def bitcount(i):
    res = 0
    while i > 0:
        res += i&1
        i>>=1
    return res

def convertToLogic(expression):
    mainResult = ""
    for vec in expression:
        varCount = 0
        result = ""
        for elem in range(len(vec[0])):
            if vec[0][elem] == "-": continue
            if vec[0][elem] == "0":result += "~"
            varCount += 1
            result += string.ascii_lowercase[elem]+"&"
        if(varCount > 1):
            mainResult += "(" + result[:-1] + ")|"
        else:
            mainResult += result[:-1] + "|"
    return mainResult[:-1]


def check(expr, binaries):
    for result in [evaluate_logic(expr, binary) for binary in binaries]: print(result)

def unate_cover(primes, minTerms):

    chart = []
    for minTerm in minTerms:
        column = []
        for i in range(len(primes)):
            #                 print(minTerm[1])
            #                 print(primes[i][1])
            if (minTerm[1][0] in primes[i][1]):
                column.append(i)
        #             print(column)
        chart.append(column)

    print(chart)

    covers = []
    if len(chart) > 0:
        covers = [set([i]) for i in chart[0]]
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
            result = primes_in_cover

    return min_complexity, result

def calculate_complexity(minterms):

    complexity = len(minterms)
    if complexity == 1:
        complexity = 0
    mask = (1 << len(minterms[1][0])) - 1
    for minterm in minterms:
        masked = ~minterm[1][1] & mask
        #            print(masked)
        term_complexity = bitcount(masked)
        #            print(term_complexity)
        if term_complexity == 1:
            term_complexity = 0
        complexity += term_complexity
        complexity += bitcount(~minterm[1][1] & masked)

    return complexity


def main():
    binaries = read_data("data.txt")
    binaries = {"000", "001", "010", "101", "110", "111"}
    # print(binaries)
    parsed_binaries = parse_minterms(binaries)
    print()
    result = quine_mc_cluskey(parsed_binaries)
    # print(result)
    print()
    expr = convertToLogic(result)
    #    print(expr)
    # {'-10', '~-~', '0-0', '11-', '00-', '1-1', '~~-', '-01', '-^^'}
    r = [['~-~', [2, 0, 5, 7]], ['00-', [0, 1]], ['1-1', [5, 7]], ['-01', [1, 5]], ['11-', [6, 7]], ['0-0', [2, 0]],
         ['~~-', [0, 1, 6, 7]], ['-⨀⨀', [2, 6, 1, 5]], ['-10', [2, 6]]]
    print(r)
    x, y = unate_cover(r, parsed_binaries)
    print(y)


def minimize():
    # temporary input of expression
    expr = "(a|b)|(c|a|b)"
    variables = gev_variables(expr)
    b = binary_generator(len(variables))
    min_terms = [minTerm for minTerm in b if evaluate_logic(expr, minTerm)]
    parsed_min_terms = parse_minterms(min_terms)
    primes = quine_mc_cluskey(parsed_min_terms)
    expr = convertToLogic(primes)
    print(expr)



minimize()




