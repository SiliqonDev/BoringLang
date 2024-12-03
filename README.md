> # BoringLang
### A programming language i work on when im bored

(outdated documentation)
# Operators

* The language currently has the following binary operators: +, -, *, **, %, /, //, and, or, !=, ==, >=, <=, >, <

* and the following unary operators: not, -

* and the = assignment operator

* All operations immediately return the resulting value

# Data types
### The language has the following datatypes

> ### Number
* A number can be a float or an integer

* All operations can be performed on numbers

> ### Boolean

* A boolean can be true or false, they are represented by `1` and `0` respectively

```
boring > true
1
boring > false
0
boring > true + false
1
```

> ### String

A string is any collection of ascii characters encased in `" "` (double quotes) or `' '` (single quotes)
* An empty string has no characters ("")
* A string can contain any ascii characters
* Strings can be concatenated using the `+` operator or multiplied using the `*` operator
* Any character immediately after a `\` will be treated as an escape character

Example -
```
boring > var s = "Hello world!"
'Hello world!'

boring > s + " 123"
'Hello world! 123'
boring > s*3
'Hello world!Hello world!Hello world!'

boring > var other = "\"Woo!\"\nNice"
'"Woo!"
Nice'

boring > 'a' + (var c = 'c')
'ac'
```

> ### List
A list is an ordered sequence of elements
* Lists can contain values of any datatype inside it
* Lists in BoringLang are 0-indexed, access an index by putting it within `(` and `)`
* The language currently uses the `+` operator to append elements to a list and `*` to multiply them

Example -
```
boring > var myList = [1,2,3]
[1, 2, 3]
boring > myList*2
[1, 2, 3, 1, 2, 3]

boring > myList + [4,5]
[1, 2, 3, [4, 5]]

boring > myList(1)
2

boring > var secList = myList + 4 + [5,6] + (var a = 10) + (fn hello() -> "hello") + (for i = 1 to 5 do i)
[1, 2, 3, 4, [5, 6], 10, <function hello>, [1, 2, 3, 4]]

boring > a
10
boring > secList(1)
2
boring > secList(4)
[5,6]
boring > (secList(6))()
hello
```

# Variables
Variables are assigned using the `var` keyword, an identifier, and the `=` assignment operator
* A variable can be defined as any datatype or value
* Variable definitions also immediately return the value of the variable
```
boring > var a = 3
3
boring > var b = 10
10

boring > a + b
13
```
Operations on variables
```
boring > a - b
-7
boring > 10 * a + b
40

boring > b + (var c = 5)
15
boring > c
5

boring > a % 2
1
```

# Conditional Statements

Conditional statments check for the given condition and may or may not return a value, depending on the statement

* BoringLang has the following comparison operators: !=, ==, >=, <=, > and <
* All comparison operators return values in boolean datatype
* BoringLang has the if, elif, and else conditional statements

```
boring > var a = 3
3
boring > var b = 9
9

boring > if a != 3 then b elif a == 3 then b+1 else b+2
10

boring > a <= 3
1

boring > (b//3) == 3
1

boring > a > 3 and b < 10
0

boring > a == 4 or b > 8
1

boring > if not 3 then b
(no output)

boring > if a == 2 then 3*13 else not b
0
```

# Functions
Functions can be used to run a chunk of code from anywhere else
* Functions return themself when defined
* Functions return a value if the code in it returns a value
* Each function has its own inside scope for variables, however if it does not find the desired variable then it looks in an outside scope

```
boring > var a = 2
boring > var b = 5

boring > fn add(a,b) -> a + b
<function add>
boring > var mulref = fn mul(a,b) -> a*b
<function mul>
boring > var addref = add
<function add>

boring > add(a,b)
7
boring > add(a,10)
12
boring > mulref(2,3)
6
boring > mul(2,3)
6
```
Here, the function looks in the parent scope for the variables 'a' and 'b'
```
boring > fn third() -> a + b
<function third>
boring > third()
7
boring > var a = 10
10
boring > third()
15
```

Functions can also be used inside other functions
```
boring > fn is_one(n) -> if n == 1 then 1 else 0
<function is_one>
boring > fn div_by_3_is_one(n) -> if is_one(n//5) then 1 else 0
<function div_by_3_is_one>
boring > is_one(3)
0
boring > is_one(1)
1
boring > div_by_3_is_one(3)
1
boring > div_by_3_is_one(5)
0
```

Functions do not need to have a name, however, these functions cannot be called
```
boring > fn (a,b,c) -> a + b + c
<function <anonymous>>
(this function can never be called since it does not have a name)
```

A function can also return other functions

```
boring > fn first(n) -> (fn second(n) -> n+1)
<function first>
boring > first(1)
<function second>
boring > (first(1))(1)
2
boring > second(1)
(this will error, as <function second> does not exist in the global scope, it only exists when returned by <function first>)
```
It is recommended to return nameless functions in this case
```
boring > fn first() -> (fn (n) -> n + 1)
<function first>
boring > first()
<function <anonymous>>
boring > (first())(2)
3
```

# Loops

A loop runs the code in the body of the loop as long as the given condition is met

* For loops can be given a starting value, ending value, and step value

* While loops must be given a condition, the loop runs as long as the condition is met

* Once completed, loops return a List containing all values returned by the body code in each iteration, in order

```
boring > var a = 1
1

boring > for i = 1 to 6 do var a = a * i
[1, 2, 6, 24, 120]
boring > a
120

boring > var odd_sum = 0
0
boring > for i = 1 to 10 step 2 do var odd_sum = odd_sum + i
[1, 4, 9, 16, 25]
boring > odd_sum
25

boring > var b = 4
4
boring > while b <= 8 do var b = b * 2
[8, 16]
boring > b
16
```

Loops can also utilize functions for more complex conditions
```
boring > fn complex_maths(n) -> n**2
<function complex_maths>
boring > for i = 1 to 5 do complex_maths(i)
[1, 4, 9, 16]
```

## TODO
- External file support
- Comments
- return, break, continue
- maps and stuff etc.
- remove 'var' from variable definition
- and more...
