"""
Name:
Class: Principles of Computing
"""
import os
import re
import sys


def is_nonterminal(string):
    """
    :param string: Accepts a lexeme string
    :return: True if lexeme is nonterminal
    """
    return isinstance(string, str) and re.match(r"^<.*>$", string) is not None


# match searching from the beginning of the string a < followed by any number of characters
# and ended with a >
# re.match returns none if no match.

def is_terminal(string):
    """
    :param string: Accepts a lexeme string
    :return: True if lexeme is terminal
    """
    return isinstance(string, str) and not is_nonterminal(string)


def is_sentence(sentence):
    """
    :param sentence: Accepts a string sentence or a sentence in list form
    :return: Returns true if the sentence has no nonterminals
    """
    if isinstance(sentence, str):
        return not re.search(r"<.*>", sentence)

    if isinstance(sentence, list):
        sent = " ".join(sentence)
        return not re.search(r"<.*>", sent)

    raise Exception("is_sentence() argument is not a string or a list")


def input_sentence():
    """
    User is prompted to enter a sentence.
    :return: sentence in a str
    """
    while True:
        sentence = input("Enter a sentence\n")
        if not is_sentence(sentence):
            # I did it like this to avoid pylint flagging it
            print("Invalid sentence, try again. Sentence should"
                  "not have any nonterminals")
        else:
            # Remove excess whitespace to format the sentence
            return ' '.join(sentence.split())


def compare(sentence, sentential):
    """
    :param sentence: Final sentence in a list or a string
    :param sentential: sentential form in a list or a string
    :return: How many lexemes in the sentential form matches the final sentence
    starting from the left and going to the right
    """
    match_count = 0
    if isinstance(sentence, str):
        first = sentence.split()
    elif isinstance(sentence, list):
        first = sentence.copy()
    else:
        raise Exception("Compare() arguments are not strings or lists")
    if isinstance(sentential, str):
        second = sentential.split()
    elif isinstance(sentential, list):
        second = sentential.copy()
    else:
        raise Exception("Compare() arguments are not strings or lists")

    size = len(first)
    for index in range(size):
        if index < len(second) and first[index] == second[index]:
            match_count += 1
        else:
            break

    return match_count


def find_first_nonterminal(sentential):
    """
    :param sentential: receives a sentential form in a string or a list
    :return: finds and returns the first nonterminal in a string.
    If there are no nonterminals, returns None
    """
    if isinstance(sentential, str):
        lexemes = sentential.split()
    elif isinstance(sentential, list):
        lexemes = sentential.copy()
    else:
        raise Exception("find_first_nonterminal() argument is not string or list")
    for item in lexemes:
        if is_nonterminal(item):
            nonterm = item
            return nonterm
    return None


def new_terminal(rule_tuple):
    """
    :param rule_tuple: A rule in form of a tuple
    :return: True if substituting the rule results in a new terminal
    """
    if not isinstance(rule_tuple, tuple):
        raise Exception("new_terminal() wrong argument type")

    rhs = rule_tuple[1]
    return is_terminal(rhs[0])


def substitute(rule_tuple, sentential):
    """
    :param rule_tuple: A rule in form of a tuple
    :param sentential: The sentential string or list to substitute the rule in
    :return: substitutes the rule into the sentential and returns the string
    """
    if not isinstance(rule_tuple, tuple):
        raise Exception("substitute() wrong argument type")

    if isinstance(sentential, str):
        sent = sentential.split()
    elif isinstance(sentential, list):
        sent = sentential.copy()
    else:
        raise Exception("substitute() wrong argument type")

    lhs = rule_tuple[0]  # <foo>
    rhs = rule_tuple[1]  # list of rules to replace <foo>
    # to substitute in the rhs
    length = len(sent)
    index = None
    for i in range(length):
        if sent[i] == lhs:
            index = i
            break
    if index is None:
        # raise Exception("Substitute() no match in sentential to substitute")
        return False
    temp = []
    copy = sent.copy()
    counter = 0
    for i in range(index, length):
        temp.append(copy[i])  # copies over starting at the replacement index
        counter += 1

    temp.pop(0)  # remove the first item which is what gets replaced

    for i in range(counter):  # remove the same amount as copied over
        copy.pop()

    copy.extend(rhs)  # paste the rule in
    copy.extend(temp)  # paste all the temporarily removed items back
    return ' '.join(copy)


def find_rule(nonterminal, grammar_rules):
    """
    :param nonterminal: Accepts a nonterminal str
    :param grammar_rules: Accepts a list of grammar rules
    :return: List of all rules that match the nonterminal
    """
    list_matches = []
    for item in grammar_rules:
        if item[0] == nonterminal:
            list_matches.append(item)
    return list_matches


def read_grammar(filepath):
    """
    :param filepath: Path to grammar file
    :return: A list with all the grammars
    """
    grammar = []
    current_lhs = None

    def make_rule(lhs, rhs):
        """
        :param lhs: the left hand side of the rule
        :param rhs: the remaining right hand side of the rule
        :return: lhs and rhs if both are valid
        """
        if is_terminal(lhs):
            # Left hand side cannot be a terminal
            raise Exception("LHS {} is a terminal".format(lhs))
        if len(rhs) == 0:  # If missing right hand side
            raise Exception("Empty RHS")
        return lhs, rhs  # returns the lhs and rhs to be appended into rules

    def parse_rhs(lexeme):
        """
        :param lexeme: A list of lexemes from a single line
        :return: A list "rules" of the extracted and validated rules from the list of lexemes
        """
        rules = []
        rhs = []
        for lex in lexeme:
            if lex == "|":
                rules.append(make_rule(current_lhs, rhs))
                rhs = []
            else:
                rhs.append(lex)
        rules.append(make_rule(current_lhs, rhs))  # Checks if rule is valid
        return rules  # Returns a list of rules to be extended into grammar list

    with open(filepath) as file:
        for line in file:
            lexemes = line.split()
            if not lexemes:  # If empty line
                pass
            elif len(lexemes) == 1:
                raise Exception("Illegal rule {}".format(line))
            elif is_nonterminal(lexemes[0]) and lexemes[1] == "->":  # Potential rule
                # If the first lexeme is nonterminal and followed by a -->
                current_lhs = lexemes[0]
                grammar.extend(parse_rhs(lexemes[2:]))
                # Attempt to extend grammar with elements past the -->
            elif lexemes[0] == "|":
                grammar.extend(parse_rhs(lexemes[1:]))
                # Attempt to extend grammar with elements past the |
            else:
                raise Exception("Illegal rule {}".format(line))

    return grammar


def print_grammar(grammar):
    """
    :param grammar: A list of BNF grammar rules
    :return: Does formatted print out of all the rules
    """
    for rule in grammar:
        print("{} -> {}".format(rule[0], " ".join(rule[1])))


def print_derivation(deriv):
    """
    :param deriv: A table of the derivation for a sentence
    :return: Prints the full derivation
    """
    counter = 1
    size = None
    done = False
    for item in deriv:
        if counter == 1:
            size = len(item) + 2
            print(counter, ": ", sep="", end="")
            print(item, "-> ", end="")
            counter += 1
            continue
        if counter == 2 and not done:
            print(item)
            done = True
            continue
        print(counter, ":", sep="", end="")
        if counter in (10, 100, 1000, 10000):
            size -= 1
        print(" " * size, sep="", end="")
        print("->", item)
        counter += 1


def main():
    """
    Reads in a BNF grammar. Accepts a sentence and attempts left-most derivation of the sentence
    using the given BNF grammar
    :return: left-most derivation of a sentence with a given grammar
    """
    if len(sys.argv) == 1:
        filepath = input("Enter path of input grammar.\n")
    else:
        filepath = sys.argv[1]

    if not os.path.isfile(filepath):
        raise Exception("File path {} does not exist.".format(filepath))

    print("Reading grammar from {}".format(filepath))
    grammar = read_grammar(filepath)
    print_grammar(grammar)
    while True:
        sentence = input_sentence()
        derivation_table = []
        if derivation(grammar, derivation_table, sentence):
            print("Derivation of:", sentence)
            print_derivation(derivation_table)
        else:
            print("No derivation found")
        if input("Enter another sentence (y/n)?: ") in ('y', 'Y'):
            continue
        print("Ending program")
        return 0

def derivation(grammar, derive_table, sentence):
    """
    :param grammar: A list of grammar rules
    :param derive_table: Empty table
    :param sentence: Sentence to derive
    :return: True if derivation is found. Places derivation in derive_table
    """
    # Initialize with the first item
    grammar_copy = grammar.copy()
    size = len(grammar_copy)
    for i in range(size):
        grammar_copy[i] += ([int(0)],)  # Adds a counter to each rule
    curr_sentential = "" + grammar_copy[0][0]
    start_match = compare(sentence, curr_sentential)

    def recursion_matching(grammar_copy, curr, match):
        """
        :param grammar_copy: Grammar with counter for each rule
        :param curr: Current sentence
        :param match: A score of how close the match is
        :return: True if a derivation is found. If it is found
                 the derive_table is appended with the derivation
        """
        def reset_rule_count(current_rule, rule_list):
            """
            :param current_rule: Rule used
            :param rule_list: List of rules
            :return: Resets the counter on the rule to 0
            """
            size = len(rule_list)
            for index in range(size):
                if rule_list[index][0] == current_rule[0] and \
                        rule_list[index][1] == current_rule[1]:
                    rule_list[index][2].pop()
                    rule_list[index][2].append(0)

        def increment_rule_count(current_rule, rule_list):
            """
            :param current_rule: tuple of current rule
            :param rule_list: list of all the rule
            :return: increment the counter of the matching rule in the list of rules
            """
            size = len(rule_list)
            for index in range(size):
                if rule_list[index][0] == current_rule[0] and \
                        rule_list[index][1] == current_rule[1]:
                    count = rule_list[index][2].pop()
                    rule_list[index][2].append(count + 1)

        def least_used_rule(current_rule, rule_list):
            """
            :param current_rule: Tuple of rule to be checked
            :param rule_list: List of all the rules
            :return: True if no other rules have been used significantly
                     less than current_rule
            """
            size = len(rule_list)
            flex = len(sentence.split())
            if size == 1:
                return True
            for index in range(size):
                if rule_list[index][0] == current_rule[0] and \
                        rule_list[index][1] == current_rule[1]:
                    pass
                elif rule_list[index][2][0] < current_rule[2][0] - flex:
                    # Flex is how out of balance usage of one rule over the other can be
                    # before it forces the recursion to try the less used one.
                    # Higher flex = more flexibility, but slower. Some problems have the
                    # same rule applied over and over while others have more balance usage
                    # of each rule. There has to be some sort of flex limitation
                    # The program cannot be allowed to recursively try the same rule
                    # over infinitely, yet the program needs to be flexible enough to
                    # apply the same rule multiple times in order to get a derivation
                    # Long sentences may need high flex value to calculate successfully
                    # So flex is based off the length of the sentence
                    return False
            return True

        # Start of def recursion_matching(grammar_copy, curr, match):
        if is_sentence(curr):
            if curr == sentence:
                derive_table.append(curr)
                return True
            return False
        current_match = match
        rules = find_rule(find_first_nonterminal(curr), grammar_copy)
        if len(curr.split()) > len(sentence.split()) + 1:
            # if the current string is 10 elements longer than the sentence, give up on it
            # The longer current string is wrong anyways so stop wasting computing power
            return False

        for i in rules:
            if not least_used_rule(i, rules):
                # Must use all rules in a balanced way
                # continue on and use another rule
                continue
            newterm = new_terminal(i)
            temp = substitute(i, curr)
            increment_rule_count(i, grammar_copy)
            new_match = compare(sentence, temp)
            if not newterm:
                if recursion_matching(grammar_copy, temp, current_match):
                    derive_table.append(curr)
                    return True
            elif newterm and new_match > current_match:
                if recursion_matching(grammar_copy, temp, new_match):
                    derive_table.append(curr)
                    return True
        for i in rules:
            # We want to reset the counter used to balance all the rule used
            # in the current recursion so it does not mess up the balance in
            # the rest of the remaining recursion
            reset_rule_count(i, rules)
        return None

    if recursion_matching(grammar_copy, curr_sentential, start_match):
        derive_table.reverse()
        return True
    return False


if __name__ == "__main__":
    main()
