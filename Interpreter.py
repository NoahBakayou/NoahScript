def build_program_map(lines):
    stack = []
    program_map = {}
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith("START_"):
            stack.append(i)
        elif line.startswith("END_"):
            start_index = stack.pop()
            program_map[start_index] = i
            program_map[i] = start_index
            if line == "END_IF" and i + 1 < len(lines) and lines[i + 1].strip().startswith("START_ELSE"):
                # Directly link END_IF to START_ELSE for skipping
                program_map[i] = i + 1
                program_map[i + 1] = i  # Link START_ELSE back to END_IF for reference
    return program_map

# This function takes the entire program as a string and returns a structured list.
def parse_program(program):
    lines = program.splitlines()  
    structured_program = [] 
    i = 0  # Initialize i to 0 before the while loop

    while i < len(lines):  
        line = lines[i].strip() 

        if line.startswith("START_"):  
            
            block_type = line.split()[0][6:]  
            
            block_content, i = extract_block(lines, i, block_type)
            
            structured_program.append((block_type, block_content))
        else:
            structured_program.append(("LINE", line))
        i += 1 

    return structured_program

def extract_block(lines, start_index, block_type):
    block_lines = []  # Initialize an empty list to hold lines of the current block.
    end_marker = "END_" + block_type  # Define the end marker for the current block type.
    i = start_index + 1  # Set the starting index to the line after the block's start marker.
    depth = 1  # Initialize depth to 1 to account for the current block.

    # Iterate over lines until the matching end marker for the current block is found, adjusting for nested blocks.
    while i < len(lines) and depth > 0:
        line = lines[i].strip()  # Strip whitespace from the current line for processing.
        
        if line.startswith("START_"):
            depth += 1  # Increase depth for each nested START_, indicating a new nested block.
        elif line == end_marker:
            depth -= 1  # Decrease depth for each END_ that matches the block type, indicating the end of a nested block.

        if depth == 0:
            # If depth reaches 0, the end marker for the outermost block has been found.
            break  # Exit the loop since the end of the current block has been reached.
        if depth > 0:
            # As long as the current depth is greater than 0, add the line to block_lines, excluding the final END_ marker.
            block_lines.append(line)
            
        i += 1  # Move to the next line to continue processing.

    return block_lines, i  # Return the collected lines within the block and the index of the last processed line.



def varmap(targetVar, state):
        return state.get(targetVar, 0)

def tokenize(expression):
    tokens = []
    current_token = ""
    i = 0  # Initialize i here for proper use in the loop
    while i < len(expression):  # Use while loop to iterate through characters
        char = expression[i]
        if char.isspace():
            if current_token:
                tokens.append(current_token)
                current_token = ""
        elif char in "+-*/()%":
            if current_token:
                tokens.append(current_token)
            tokens.append(char)
            current_token = ""
        elif i + 1 < len(expression):  # Check next character for multi-character operators
            if char == '=' and expression[i + 1] == '=':
                tokens.append('==')
                i += 1  # Skip the next character
            elif char == '!' and expression[i + 1] == '=':
                tokens.append('!=')
                i += 1
            elif char == '<' and expression[i + 1] == '=':
                tokens.append('<=')
                i += 1
            elif char == '>' and expression[i + 1] == '=':
                tokens.append('>=')
                i += 1
            elif char == '<':
                tokens.append('<')
            elif char == '>':
                tokens.append('>')
            else:
                current_token += char
        else:
            current_token += char
        i += 1

    if current_token:
        tokens.append(current_token)
    return tokens

def parse_expression(tokens, index, state):
    precedence = {'*': 3, '/': 3, '%': 3, '+': 2, '-': 2, '==': 1, '!=': 1, '<=': 1, '>=': 1, '<': 1, '>': 1}
    operand_stack = []
    operator_stack = []

    while index < len(tokens):
        token = tokens[index]
        index += 1

        if token.isdigit():
            operand_stack.append(int(token))
        elif token in precedence:
            while operator_stack and precedence[operator_stack[-1]] >= precedence[token]:
                right = operand_stack.pop()
                left = operand_stack.pop()
                operand_stack.append(evaluate_operation(left, right, operator_stack.pop()))
            operator_stack.append(token)
        elif token == '(':
            result, new_index = parse_expression(tokens, index, state)
            operand_stack.append(result)
            index = new_index
        elif token == ')':
            break
        else:
            operand_stack.append(varmap(token, state))

    while operator_stack:
        op = operator_stack.pop()
        right = operand_stack.pop()
        left = operand_stack.pop()
        operand_stack.append(evaluate_operation(left, right, op))

    return operand_stack[0], index

def evaluate_operation(left, right, op):
    if op == '+':
        return left + right
    elif op == '-':
        return left - right
    elif op == '*':
        return left * right
    elif op == '/':
        if right == 0:
            raise ZeroDivisionError("Division by zero is not allowed.")
        return left / right
    elif op == '%':
        return left % right
    elif op == '==':
        return left == right
    elif op == '!=':
        return left != right
    elif op == '<=':
        return left <= right
    elif op == '>=':
        return left >= right
    elif op == '<':
        return left < right
    elif op == '>':
        return left > right


def evaluate_expression(tokens, state):
    #print(f"Evaluating expression: {tokens}")
    result, _ = parse_expression(tokens, 0, state)
    #print(f"Result of expression: {result}")
    return result

def execute_assign(command, state):
    lhs, rhs = command.split('=', 1)
    lhs = lhs.strip()
    rhs = rhs.strip()
    
    # Check if rhs is a string (starts and ends with quotes)
    if rhs.startswith('"') and rhs.endswith('"'):
        # Remove the quotes and assign the string value
        state[lhs] = rhs[1:-1]
    elif rhs.isdigit():  # Check if rhs is a digit and assign it as an integer
        state[lhs] = int(rhs)
    else:  # Assume rhs is an expression or a variable name
        tokens = tokenize(rhs)
        result = evaluate_expression(tokens, state)
        state[lhs] = result


def execute_print(command, state):
    var_name = command.strip()
    if var_name in state:
        print(state[var_name])
    else:
        print("Error: Variable not found")

def execute_if(command, state, lines, current_index, program_map):
    condition_tokens = tokenize(command)
    condition_result = evaluate_expression(condition_tokens, state)
    
    if_block_end = program_map[current_index]  # This is the END_IF line index
    next_index = if_block_end + 1  # Default next index is after END_IF
    
    if condition_result:
        # Execute the IF block
        i = current_index + 1
        while i < if_block_end:
            i = execute_command(lines[i].strip(), state, lines, i, program_map)
    else:
        # Check for ELSE block
        if if_block_end + 1 in program_map and lines[if_block_end + 1].strip().startswith("START_ELSE"):
            else_block_start = if_block_end + 1
            else_block_end = program_map[else_block_start]
            next_index = else_block_end + 1  # Adjust next_index to after END_ELSE
            # Execute the ELSE block
            i = else_block_start + 1
            while i < else_block_end:
                i = execute_command(lines[i].strip(), state, lines, i, program_map)

    return next_index

def execute_while(command, state, lines, current_index, program_map):
    condition = command.strip()
    end_while_index = program_map[current_index]  # Use program_map to find the end of the WHILE block

    initial_condition_evaluation = True
    while True:
        condition_tokens = tokenize(condition)
        condition_result = evaluate_expression(condition_tokens, state)

        if not condition_result and not initial_condition_evaluation:
            break

        initial_condition_evaluation = False
        i = current_index + 1
        while i < end_while_index:
            i = execute_command(lines[i].strip(), state, lines, i, program_map)

    return end_while_index + 1

def execute_for(command, state, lines, current_index, program_map):
    parts = command.split()
    if len(parts) != 7 or parts[1] != "FROM" or parts[3] != "TO" or parts[5] != "BY":
        print("Invalid FOR loop syntax")
        return current_index + 1
    
    var_name = parts[0]
    
    # Check and retrieve start value (either from state or directly as an int)
    start_part = parts[2]
    start_value = int(state[start_part]) if start_part in state else int(start_part)
    
    # Check and retrieve end value (either from state or directly as an int)
    end_part = parts[4]
    end_value = int(state[end_part]) if end_part in state else int(end_part)
    
    # Check and retrieve increment value (either from state or directly as an int)
    increment_part = parts[6]
    increment_value = int(state[increment_part]) if increment_part in state else int(increment_part)
    
    end_for_index = program_map[current_index]

    if increment_value == 0:
        print("Error: Increment value cannot be 0")
        return end_for_index + 1

    if (increment_value > 0 and start_value > end_value) or (increment_value < 0 and start_value < end_value):
        print("Warning: Loop start and end values indicate the loop will not execute due to the increment direction")
        return end_for_index + 1

    value = start_value
    while (increment_value > 0 and value <= end_value) or (increment_value < 0 and value >= end_value):
        state[var_name] = value
        i = current_index + 1
        while i < end_for_index:
            i = execute_command(lines[i].strip(), state, lines, i, program_map)
        value += increment_value

    return end_for_index + 1

def execute_command(command, state, lines, current_index, program_map):
    #print(f"About to execute command: {command}")
    if not command.strip():
        return current_index + 1

    if command.startswith("ASSIGN"):
        execute_assign(command[len("ASSIGN"):].strip(), state)
    elif command.startswith("PRINT"):
        execute_print(command[len("PRINT"):].strip(), state)
    elif command.startswith("START_IF"):
        return execute_if(command[len("START_IF"):].strip(), state, lines, current_index, program_map)
    elif command.startswith("START_ELSE"):  # Ignore START_ELSE since its logic is handled in execute_if
        return program_map[current_index] + 1
    elif command.startswith("EASTER_EGG"):
        print("🐰 You found the Easter Egg! 🥚🌷")
    elif command in ["END_IF", "END_ELSE", "END_WHILE", "END_FOR"]:
        return current_index + 1  # Move to the next command
    elif command.startswith("START_WHILE"):
        return execute_while(command[len("START_WHILE"):].strip(), state, lines, current_index, program_map)
    elif command.startswith("START_FOR"):
        return execute_for(command[len("START_FOR"):].strip(), state, lines, current_index, program_map)
    else:
        print(f"Unknown command: {command}")
    return current_index + 1

def executeProgram(program):
    state = {}
    lines = program.splitlines()
    program_map = build_program_map(lines)  # Generate the program map
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        i = execute_command(line, state, lines, i, program_map)


sampleProgram = """
ASSIGN maxNum = 16
ASSIGN counter = 5
ASSIGN FizzBuzz = "FizzBuzz"
ASSIGN Fizz = "Fizz"
ASSIGN Buzz = "Buzz"
ASSIGN Countdown = "Countdown:"

START_FOR i FROM 1 TO maxNum BY 1
    START_IF i % 15 == 0
        PRINT FizzBuzz
    END_IF
    START_ELSE
        START_IF i % 3 == 0
            PRINT Fizz
        END_IF
        START_ELSE
            START_IF i % 5 == 0
                PRINT Buzz
            END_IF
            START_ELSE
                PRINT i
            END_ELSE
        END_ELSE
    END_ELSE
END_FOR

PRINT Countdown
START_WHILE counter > 0
    PRINT counter
    ASSIGN counter = counter - 1
END_WHILE
EASTER_EGG
"""

executeProgram(sampleProgram)