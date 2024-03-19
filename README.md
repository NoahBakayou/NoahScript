# Program Documentation

This document provides an overview of each function within the scripting language interpreter. The interpreter is designed to parse and execute a simple script, handling variable assignments, conditional statements, loops, and print operations.

## `build_program_map(lines)`
- Generates a mapping between the start and end points of control structures (if-else blocks, loops) for efficient execution flow control.
- Utilizes a stack to track opening and closing of control blocks, allowing for nested structure support!
- Special handling for directly linking `END_IF` to `START_ELSE` to facilitate skipping in the execution flow.
- **Example:** In a sequence of `START_IF`, `END_IF`, `START_ELSE`, `END_ELSE`, `END_IF` would map to the line right after `END_IF` (the `START_ELSE` line), creating a direct jump point.

## `parse_program(program)`
- Splits the program into lines and categorizes each as a part of a control block or a standalone line, structuring the program for easier execution.
- Leverages `extract_block` for handling nested control blocks, ensuring all content is appropriately categorized.

## `extract_block(lines, start_index, block_type)`
- Extracts the contents of control blocks, correctly handling nested blocks through a depth counter.
- Iterates from the start of a block until its end, skipping nested blocks' content to correctly identify the block's end.
- Designed to work recursively, allowing for the extraction of blocks within blocks.

## `varmap(targetVar, state)`
- Retrieves the value of a variable from the current program state, returning a default value if the variable does not exist.
- Essential for handling variables that may not have been initialized, preventing errors in variable access.

## `tokenize(expression)`
- Breaks down an expression into a series of tokens (numbers, operators, variables) for easier parsing and evaluation.
- Handles multi-character operators (like `==`, `!=`, `>=`, `<=`) by grouping them into single tokens.
- Important for the evaluation process, ensuring expressions are correctly interpreted and executed.

## `parse_expression(tokens, index, state)`
- Parses a tokenized expression, applying operator precedence to evaluate the expression correctly.
- Utilizes a stack for operators and operands, allowing for the handling of nested expressions and precedence rules.
- Operator precedence is defined in a dictionary, guiding the evaluation order of operations.

## `evaluate_operation(left, right, op)`
- Performs a specific arithmetic or logical operation on two operands, based on the operator provided.
- Handles basic arithmetic (`+`, `-`, `*`, `/`, `%`) and comparison operators (`==`, `!=`, `<`, `<=`, `>`, `>=`).
- Includes error handling, like preventing division by zero.

## `evaluate_expression(tokens, state)`
- Evaluates a tokenized expression to a single value, utilizing `parse_expression` for handling the logic of evaluation.
- Acts as a bridge between tokenization and the final evaluation of expressions within the program.

## `execute_assign(command, state)`
- Processes assignment commands, updating the program state with new or modified variable values.
- Distinguishes between direct value assignments and expressions, handling each appropriately.

## `execute_print(command, state)`
- Executes print commands, outputting the value of variables or expressions to the console.
- Looks up variable values in the current state, displaying errors for undefined variables.

## `execute_if(command, state, lines, current_index, program_map)`
- Manages the execution flow of if statements, including condition evaluation and jumping to else blocks if necessary.
- Utilizes `program_map` for navigating to the correct next point in the program, depending on the condition's outcome.

## `execute_while(command, state, lines, current_index, program_map)`
- Implements while loops, repeating a block of code as long as the condition evaluates to true.
- Uses `program_map` to find the loop's end and to repeat execution from the start of the loop until the condition fails.

## `execute_for(command, state, lines, current_index, program_map)`
- Handles for loops, iterating over a range of values and executing a block of code for each iteration.
- Parses the loop's parameters (start, end, step) and manages the loop's execution based on these values.

## `execute_command(command, state, lines, current_index, program_map)`
- The main dispatcher for executing commands within the program.
- Determines the type of command (assignment, print, control structure) and calls the appropriate function to handle it.

## `executeProgram(program)`
- The entry point for executing the provided program script.
- Initializes the program state, parses the program into a structured format, and sequentially executes each command.
