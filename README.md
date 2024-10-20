# BoringLang
 A programming language i work on when im bored


# Super bare bones documentation
## Variables

Variable definitions also immediately return the value of the variable

```
boring > var a = 3
3
boring > var b = 10
10

boring > a + b
13
```

## Operations on variables

The language currently has the following binary operators: +, -, *, ^, /, //, and, or, ==, >=, <=, >, <

and the following unary operators: not, -

and the = assignment operator

All operations immediately return the resulting value

```
var a = 7
var b = 19

boring > a * b 
133

boring > a / b
0.368....

boring > a + b
26

boring > a - b
-12

boring > b ^ a 
893871739

boring > a * (var c = 10)
70

boring > c
10

boring > (a + b) * c
260

boring > a + 10 * c
107
```

## Conditional Statements

Conditional statments return the final value immediately

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

boring > not a
0

boring > not 0
1

boring > if not 3 then b
(no output)

boring > if a == 2 then 3*13 else not b
0
```

## Functions

Functions return themself when defined

Functions return a value if the code in it returns a value

Each function has its own inside scope for variables, however if it does not find the desired variable then it looks in an outside scope

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

boring > fn third() -> a + b
<function third>
boring > third()
7
boring > var a = 10
10
boring > third()
15

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

## Loops

Loops do not return a value, they simply iterate and execute the code inside as long as their condition is true

```
boring > var a = 1
1

boring > for i = 1 to 6 do var a = a * i
(no output as loops do not return anything)
boring > a
120

boring > var odd_sum = 0
0
boring > for i = 1 to 10 step 2 do var odd_sum = odd_sum + i
boring > odd_sum
25

boring > var b = 4
4
boring > while b <= 8 do var b = b * 2
(no output as loops do not return anything)
boring > b
16

boring > fn is_over_zero(n) -> if n > 0 then 1 else 0
<function is_over_zero>
boring > var c = 3
3
boring > while is_over_zero(c) do var c = c - 1
boring > c
0
```


## TODO
- External file support
- Comments
- return, break, continue
- strings, lists, tuples, maps, etc.
- remove 'var' from variable definition
- and more...