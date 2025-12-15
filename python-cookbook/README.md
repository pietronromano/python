# Modern-Python-Cookbook-Third-Edition
Code Repository for Modern Python Cookbook Third Edition, Published by Packt

SOURCE: https://github.com/PacktPublishing/Modern-Python-Cookbook-Third-Edition

---

# Table of Contents
1.	Chapter 1: Numbers, Strings, and Tuples
1.1	Choosing between float, decimal, and fraction
1.2	Choosing between true division and floor division
1.3	String parsing with regular expressions
1.4	Building complicated strings with f-strings
1.5	Building complicated strings from lists of strings
1.6	Using the Unicode characters that aren’t on our keyboards
1.7	Encoding strings – creating ASCII and UTF-8 bytes
1.8	Decoding bytes – how to get proper characters from some bytes
1.9	Using tuples of items
1.10	Using NamedTuples to simplify item access in tuples
2.	Chapter 2 Statements and Syntax
2.1	Writing Python script and module files – syntax basics
2.2	Writing long lines of code
2.3	Including descriptions and documentation
2.4	Writing better docstrings with RST markup
2.5	Designing complex if...elif chains
2.6	Saving intermediate results with the := ”walrus” operator
2.7	Avoiding a potential problem with break statements
2.8	Leveraging exception matching rules
2.9	Avoiding a potential problem with an except: clause
2.10	Concealing an exception root cause
2.11	Managing a context using the with statement
3.	Chapter 3: Function Definitions
3.1	Function parameters and type hints
3.2	Designing functions with optional parameters
3.3	Using super flexible keyword parameters
3.4	Forcing keyword-only arguments with the * separator
3.5	Defining position-only parameters with the / separator
3.6	Picking an order for parameters based on partial functions
3.7	Writing clear documentation strings with RST markup
3.8	Designing recursive functions around Python’s stack limits
3.9	Writing testable scripts with the script-library switch
4.	Chapter 4: Built-In Data Structures Part 1: Lists and Sets
4.1	Choosing a data structure
4.2	Building lists – literals, appending, and comprehensions
4.3	Slicing and dicing a list
4.4	Shrinking lists – deleting, removing, and popping
4.5	Writing list-related type hints
4.6	Reversing a copy of a list
4.7	Building sets – literals, adding, comprehensions, and operators
4.8	Shrinking sets – remove(), pop(), and difference
4.9	Writing set-related type hints
5.	Chapter 5: Built-In Data Structures Part 2: Dictionaries
5.1	Creating dictionaries – inserting and updating
5.2	Shrinking dictionaries – the pop() method and the del statement
5.3	Writing dictionary-related type hints
5.4	Understanding variables, references, and assignment
5.5	Making shallow and deep copies of objects
5.6	Avoiding mutable default values for function parameters
6.	Chapter 6: User Inputs and Outputs
6.1	Using the features of the print() function
6.2	Using input() and getpass() for user input
6.3	Debugging with f”{value=}” strings
6.4	Using argparse to get command-line input
6.5	Using invoke to get command-line input
6.6	Using cmd to create command-line applications
6.7	Using the OS environment settings
7.	Chapter 7: Basics of Classes and Objects
7.1	Using a class to encapsulate data and processing
7.2	Essential type hints for class definitions
7.3	Designing classes with lots of processing
7.4	Using typing.NamedTuple for immutable objects
7.5	Using dataclasses for mutable objects
7.6	Using frozen dataclasses for immutable objects
7.7	Optimizing small objects with __slots__
7.8	Using more sophisticated collections
7.9	Extending a built-in collection – a list that does statistics
7.10	Using properties for lazy attributes
7.11	Creating contexts and context managers
7.12	Managing multiple contexts with multiple resources
8.	Chapter 8: More Advanced Class Design
8.1	Choosing between inheritance and composition – the ”is-a” question
8.2	Separating concerns via multiple inheritance
8.3	Leveraging Python’s duck typing
8.4	Managing global and singleton objects
8.5	Using more complex structures – maps of lists
8.6	Creating a class that has orderable objects
8.7	Deleting from a list of complicated objects
9.	Chapter 9: Functional Programming Features
9.1	Writing generator functions with the yield statement
9.2	Applying transformations to a collection
9.3	Using stacked generator expressions
9.4	Picking a subset – three ways to filter
9.5	Summarizing a collection – how to reduce
9.6	Combining the map and reduce transformations
9.7	Implementing “there exists” processing
9.8	Creating a partial function
9.9	Writing recursive generator functions with the yield from statement
10.	Chapter 10: Working with Type Matching and Annotations
10.1	Designing with type hints
10.2	Using the built-in type matching functions
10.3	Using the match statement
10.4	Handling type conversions
10.5	Implementing more strict type checks with Pydantic
10.6	Including run-time valid value checks
11.	Chapter 11: Input/Output, Physical Format, and Logical Layout
11.1	Using pathlib to work with filenames
11.2	Replacing a file while preserving the previous version
11.3	Reading delimited files with the CSV module
11.4	Using dataclasses to simplify working with CSV files
11.5	Reading complex formats using regular expressions
11.6	Reading JSON and YAML documents
11.7	Reading XML documents
11.8	Reading HTML documents
12.	Chapter 12: Graphics and Visualization with Jupyter Lab
12.1	Starting a Notebook and creating cells with Python code
12.2	Ingesting data into a notebook
12.3	Using pyplot to create a scatter plot
12.4	Using axes directly to create a scatter plot
12.5	Adding details to markdown cells
12.6	Including Unit Test Cases in a Notebook
13.	Chapter 13: Application Integration: Configuration
13.1	Finding configuration files
13.2	Using TOML for configuration files
13.3	Using Python for configuration files
13.4	Using a class as a namespace for configuration
13.5	Designing scripts for composition
13.6	Using logging for control and audit output
14.	Chapter 14: Application Integration: Combination
14.1	Combining two applications into one
14.2	Combining many applications using the Command design pattern
14.3	Managing arguments and configuration in composite applications
14.4	Wrapping and combining CLI applications
14.5	Wrapping a program and checking the output
15.	Chapter 15: Testing
15.1	Using docstrings for testing
15.2	Testing functions that raise exceptions
15.3	Handling common doctest issues
15.4	Unit testing with the unittest module
15.5	Combining unittest and doctest tests
15.6	Unit testing with the pytest module
15.7	Combining pytest and doctest tests
15.8	Testing things that involve dates or times
15.9	Testing things that involve randomness
15.10	Mocking external resources
16.	Chapter 16: Dependencies and Virtual Environments
16.1	Creating environments using the built-in venv
17.	Chapter 17: Documentation and Style
17.1	The bare minimum: a README.rst file
17.2	Installing Sphinx and creating documentation
17.3	Using Sphinx autodoc to create the API reference
17.4	Identifying other CI/CD tools in pyproject.toml
17.5	Using tox to run comprehensive quality checks



---

# Setting up the Development Environment
The code examples all require Python 3.12.

It's often easiest to build this by starting with a tool like ``conda`` to
install Python and create virtual environments.
Conda is not required; it's only suggested.

Using Conda:

```bash
    conda create --name cookbook3 python=3.12 --channel=conda-forge
    conda activate cookbook3
    python -m pip install -r requirements.txt
```

After this setup, the test suite is run as follows:

```bash
tox
```

Since each chapter is tested in a separate virtual environment,
the first run will take several minutes to download and install the packages.
After that, the cached virtual environments will be reused.
