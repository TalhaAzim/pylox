# How the clox bugs were found: a walkthrough

`CLOX_REVIEW.md` lists *what* is wrong. This document is about *how* the bugs were found: what I looked at, in what order, what I suspected, how I checked, and how I'd think about the fix. It follows the real order of the review, including the parts I got wrong or only understood afterwards.

Each finding has a tag like `[B3]`. The same tag appears in `CLOX_REVIEW.md` and in the `// REVIEW` comments in the source, so you can search for it to move between the three.

- **Bugs:** `[B1]` freeObject order · `[B2]` consume() · `[B3]` unary precedence · `[B4]` comment fallthrough
- **Minor:** `[M1]` `case 'f'` · `[M2]` non-static resetStack · `[M3]` chunk.h include · `[M4]` tabs
- **Tooling:** `[T1]` Makefile headers · `[T2]` sanitizers · `[T3]` gcc vs clang

Line numbers in the compiler and gdb output below are from the original code (`reference-clox` at `1e199fc`). On this branch they're shifted by the `// REVIEW` comments, so use the tags to find your place.

---

## 0. The mindset in one paragraph

A bug is a gap between what the code is *supposed* to do and what it *actually* does, so you need both sides. "Supposed to" comes from a spec: here, that's the book. "Actually" comes from running the code and reading it carefully, without assuming it does what you meant. Most of bug hunting is cheap ways of comparing the two:

1. **Can it even build?** The compiler is the first reviewer.
2. **What do the warnings say?** These are hints, not noise.
3. **Run tiny inputs whose answers you already know.**
4. **Read the code with a question in mind**, not just top to bottom.
5. **Compare with a known-good reference.**
6. **Use tools that see what you can't**: the disassembler, a debugger, sanitizers.

Each time something looks off, don't jump to the fix. List the possible explanations, pick the cheapest test that tells them apart, and run it. Only then think about the fix.

---

## 1. Get oriented before looking for bugs

I started by finding out *where you are in the book*, because that tells me what is supposed to work.

```sh
git log --oneline origin/reference-clox | head
```

The last commits say `19.4 Added string operations` and `19.5 Added capability for freeing objects`. So this is the end of **chapter 19 (Strings)**. At this point the book's clox:

- compiles **one expression** (no statements, no `print`, no variables yet);
- runs it, and `OP_RETURN` prints the result;
- supports numbers, `true`/`false`/`nil`, strings, `+ - * /`, unary `-` and `!`, and comparisons;
- frees every string object at exit (`freeObjects()`).

That shapes everything after it. **Every test program has to be a single expression**, and the "output" is whatever `OP_RETURN` prints. Something like `print 1;` isn't a valid test yet: it would fail even if the code were perfect.

> **Habit:** before hunting, write down in one sentence what the program should be able to do right now. Bugs are deviations from that sentence.

Then I read every file once, **headers first** (`common.h`, `value.h`, `object.h`, `chunk.h`, `vm.h`, `scanner.h`, …). Headers are the map: which types exist, which functions are public, who includes whom. Then the `.c` files, in data-flow order: `main.c` → `vm.c` (`interpret`) → `compiler.c` → `scanner.c`, then `chunk.c`, `value.c`, `object.c` and `memory.c`.

On this first pass I was mostly asking, for each function, *what happens when things go wrong?* That question found `[B2]` (§4). The other bugs turned up by comparing lines against the book (`[B1]`, `[B3]`) and by asking where each `switch` case goes next (`[B4]`).

---

## 2. Build it: `[B1]`

```sh
make clox
```

```
src/clox/memory.c:6:40: warning: unused parameter 'oldSize' [-Wunused-parameter]
src/clox/memory.c:21:5: error: implicit declaration of function 'freeObject';
                               did you mean 'freeObjects'? [-Wimplicit-function-declaration]
src/clox/memory.c:26:13: warning: conflicting types for 'freeObject'
src/clox/memory.c:26:13: error: static declaration of 'freeObject' follows non-static declaration
```

**Read the first error first.** Later errors are often knock-on effects of earlier ones. Here, the second error only exists because of the first.

### What does "implicit declaration" mean?

C compiles each `.c` file top to bottom, in one pass. When it meets a call like `freeObject(object)`, it needs to already know `freeObject`'s signature. That comes from a definition above the call, a prototype above it, or a prototype in an included header. Old C (C89) let you skip that: the compiler would *guess* `int freeObject()` and carry on. C99 removed that rule, but gcc still makes the guess and reports an error.

### Possible explanations

When a function "doesn't exist", the usual suspects are:

| Possibility | How to check |
|---|---|
| Typo in the name (gcc even asks *did you mean 'freeObjects'?*) | `grep -n freeObject src/clox/*` |
| Defined in another file, but no prototype in a header | Same grep: which file is it in, and is it in a `.h`? |
| Defined in this file, but **below** the call | Same grep: compare line numbers |
| Not written yet | grep finds nothing |

```sh
$ grep -n freeObject src/clox/*
src/clox/memory.c:21:    freeObject(object);
src/clox/memory.c:26:static void freeObject(Obj *object) {
src/clox/memory.h:22:void freeObjects();
```

It's defined at line 26, below the call at line 21, so it's the third case. The second error follows from that: the guess was "non-static, returns `int`", and the real thing is "`static`, returns `void`". The two contradict each other.

### Thinking about the fix

- **The right fix:** move `freeObject()` above `freeObjects()`, which is where the book puts it. Alternatively, add a prototype, `static void freeObject(Obj* object);`, near the top of the file.
- **Tempting but wrong:** deleting `static`. You'd still get an implicit declaration with the wrong return type, and you'd also make an internal helper visible to the whole program. `static` on a function means "private to this `.c` file". Keep it.
- **How to know it worked:** `make clox` builds with no errors.

### The warning I dismissed: `oldSize` unused

`reallocate()` takes `oldSize` and ignores it. That's **intentional**: the book adds the parameter now and starts using it in the garbage-collection chapter. So not every warning is a bug, but each one deserves a look and a decision. Remember this, because there's a warning I *should* have taken more seriously (§4, `[B2]`).

---

## 3. Make a scratch copy and a set of probes

To keep going, I needed a build that works. I don't want to edit your branch to explore, so I made a **throwaway copy** of the tree with only the `[B1]` fix applied, and built it on cairo. The `run-on-cairo.sh` script copies the tree there and builds it.

I also built it with **sanitizers** turned on `[T2]`:

```sh
make clox CFLAGS='-std=c99 -Wall -Wextra -Isrc/clox -g -fsanitize=address,undefined'
```

- `-fsanitize=address` (ASan) stops the program at the first out-of-bounds read or write, use-after-free or double free. When the program exits, it lists any memory that was never freed.
- `-fsanitize=undefined` (UBSan) reports undefined behaviour such as signed overflow, misaligned access or a bad shift.

They make the program a bit slower, so use them for testing, not for benchmarks.

Then I wrote **probes**: one-expression programs whose correct output I worked out by hand *before* running them. A probe is only useful if you know the answer in advance.

| Probe | Why this one | Expected |
|---|---|---|
| `-1 + 2` | unary combined with binary: precedence | `1` |
| `(1 + 2` | missing `)`: error path | compile error, exit 65 |
| `1 2` | junk after an expression: error path | compile error, exit 65 |
| `1 + 2 // c` + newline | a comment followed by a newline | `3` |
| `"a" + "b" == "ab"` | string concatenation and equality (ch. 19) | `true` |
| `"a" == 1` | equality across types | `false` |
| `1 + nil` | runtime type error | error, exit 70 |
| `-"x"` | runtime type error | error, exit 70 |
| `f`, `fo` | identifiers that start like keywords | `Expect expression.` (no variables yet) |
| `"unterminated` | scanner error | `Unterminated string.` |

Where do probes like these come from? Each chapter adds a feature, so each feature gets:
- a "happy" probe (it works);
- an "edge" probe (an empty string, a lone `f`);
- a "sad" probe (it should fail cleanly);
- and one probe where two features **interact**, such as a unary operator inside a binary expression.

Interactions are where bugs hide, because each chapter tests its own feature on its own.

Results:

```
-1 + 2              -> -3                               ✗
(1 + 2              -> 3                                ✗
1 2                 -> 1                                ✗
1 + 2 // c⏎         -> Error: Unexpected character.     ✗
everything else     -> as expected                      ✓
ASan / UBSan        -> nothing reported                 ✓
```

The failing probes weren't surprises. I'd already suspected each of them while reading, and the probes were written to check those suspicions. That's the usual loop: **read → suspect → write a probe that would fail if the suspicion is right → run it.** The next sections take the suspicions one at a time.

---

## 4. Read the error paths: `[B2]`

My question while reading the compiler was: *when the input is wrong, who notices?* In this compiler, the code that is supposed to notice is `consume()`:

```c
static void consume(TokenType type, const char *message) {
  if (parser.current.type == type) {
    advance();
    return;
  }
}
```

Read it as two paths:
- **Happy path:** the token matches, so advance and return. Fine.
- **Unhappy path:** the token doesn't match, so… we fall off the end and return. **Nothing happens.**

### Possible explanations

| Possibility | How to check |
|---|---|
| The error is reported somewhere else, e.g. by the caller | Read the callers: `grouping()` and `compile()`. Neither checks anything afterwards. |
| The author meant to do it later | Check the book: `consume()` is complete in §17.2, and it ends with `errorAtCurrent(message);` |
| A line went missing | That's the remaining option, and the book confirms it. |

**The probe that settles it:** if errors are swallowed, `(1 + 2` should *run*. It printed `3`. The disassembly (`DEBUG_PRINT_CODE` is on in `common.h`) shows the compiler produced a complete, valid-looking chunk:

```
== code ==
0000    1 OP_CONSTANT         0 '1'
0002    | OP_CONSTANT         1 '2'
0004    | OP_ADD
0005    | OP_RETURN
3
```

### The lesson I learned after the fact

The build had been printing this all along:

```
src/clox/compiler.c:82:49: warning: unused parameter 'message' [-Wunused-parameter]
```

I found the bug by reading and only noticed afterwards that the compiler had pointed straight at it. A function that takes an error message and never uses it is obviously wrong once you look. When you see "unused parameter", ask **why the function takes something it never uses**. Sometimes the answer is "it's for later" (like `oldSize`). Sometimes it's "a line is missing".

### Thinking about the fix

- **The right fix:** add `errorAtCurrent(message);` as the last line. Report the error at `current`, the token we expected but didn't get, not at `previous`.
- **Tempting but wrong:** adding a check in `grouping()`. That fixes one caller and leaves `compile()` (and every later caller) broken. When a shared helper is wrong, fix the helper.
- **How to know it worked:** `(1 + 2` gives `[line 1] Error at end: Expect ')' after expression.` and exits 65. `1 2` gives `Error at '2': Expect end of expression.` Re-run *all* the probes too, so you know nothing else changed.

---

## 5. Follow precedence through the parser: `[B3]`

This one can't be spotted by looking for something missing. You have to understand what a line *means*:

```c
static void unary() {
  TokenType operatorType = parser.previous.type;

  // Compile the operand.
  expression();
  ...
}
```

### What the Pratt parser's precedence number means

`parsePrecedence(P)` means: *parse an expression, but stop at any operator that binds more weakly than `P`.* `expression()` is `parsePrecedence(PREC_ASSIGNMENT)`, the weakest level, so it **never stops early**. It eats every operator it finds.

So for `-1 + 2`:
1. `-` is a prefix operator, so `unary()` runs.
2. `unary()` calls `expression()`, which parses **`1 + 2`**, because nothing stops it at the `+`.
3. Then `unary()` emits `OP_NEGATE` for the whole thing: `-(1 + 2)`.

My suspicion came from comparing against the book. §17.4 writes `expression()` here as a temporary step, and §17.6.1 says to change it to `parsePrecedence(PREC_UNARY)`. When the book says "we'll revisit this", that's exactly the kind of edit that gets missed.

### Picking a probe that can actually fail

I needed an input where the two groupings give **different** answers:
- `-1 + 2`: the buggy reading gives `-(3) = -3`, the correct one `(-1) + 2 = 1`. Different answers, so it's a good probe.
- `!true == false`: the buggy reading gives `!(true == false) = !false = true`, the correct one `(!true) == false = false == false = true`. The **same** answer, so it's useless. For booleans, `!(a == b)` always equals `(!a) == b`, so this probe passes whether or not the bug exists.
- `!nil == false`: the buggy reading gives `!(nil == false) = !false = true`, the correct one `(!nil) == false = true == false = false`. Different answers, so it's a good probe.

> **Habit:** before trusting a test that passed, ask "would it have failed if the bug were there?" If not, it's not testing anything.

### Watching it in the bytecode

The disassembler is the best tool for parser bugs because it shows **the order the compiler emitted things in**, and that order *is* the tree the parser built.

Current code:
```
0000    1 OP_CONSTANT         0 '1'
0002    | OP_CONSTANT         1 '2'
0004    | OP_ADD                      <- adds first...
0005    | OP_NEGATE                   <- ...then negates the sum
0006    | OP_RETURN
-3
```

With `parsePrecedence(PREC_UNARY)`:
```
0000    1 OP_CONSTANT         0 '1'
0002    | OP_NEGATE                   <- negates 1 straight away
0003    | OP_CONSTANT         1 '2'
0005    | OP_ADD
0006    | OP_RETURN
1
```

A stack machine runs instructions top to bottom, so read the listing as "do this, then this". `NEGATE` after `ADD` means negation is applied to the sum.

### Thinking about the fix

- **The right fix:** `parsePrecedence(PREC_UNARY);`. The operand may contain only things that bind at least as tightly as a unary operator: literals, groupings, other unary operators (`- -1` still works, because prefix rules ignore the precedence limit), and later calls and `.` property access.
- **Tempting but wrong:** `parsePrecedence(PREC_ASSIGNMENT)`. That's just `expression()` again under another name.
- **How to know it worked:** all three probes above give the correct answer, and the disassembly shows `OP_NEGATE` right after its operand.

---

## 6. Ask where every `case` goes next: `[B4]` and `[M1]`

`switch` in C has a trap: **cases fall through**. When a case's code ends without `break` or `return`, execution carries on into the *next* case's code. This is legal, and occasionally useful, so the compiler doesn't stop you.

When reading a `switch`, I ask of every case: *when this case is done, where does control go?*

```c
static void skipWhiteSpace() {
  for (;;) {
    char c = peek();
    switch (c) {
    ...
    case '/':
      if (peekNext() == '/') {
        // A comment goes until the end of the line.
        while (peek() != '\n' && !isAtEnd())
          advance();
      } else {
        return;
        break;          // can never run: we just returned
      }
                        // <- the comment path ends up here. Where next?
    default:
      return;           // <- here. Falls through into default.
    }
  }
}
```

The comment loop stops **on** the `'\n'`, without consuming it. With a `break`, the `for (;;)` would loop again, and `case '\n'` would consume the newline and bump `scanner.line`. Without it, control falls into `default: return;`, and `skipWhiteSpace()` returns while sitting on the newline.

### Prediction, then probe

**Prediction:** `scanToken()` will try to scan `'\n'` as a token. No `case` in its `switch` handles it, so it'll return `Unexpected character.` And the line number will still be 1, because the code that increments it never ran.

**Probe:** `1 + 2 // a comment` followed by a newline → `[line 1] Error: Unexpected character.` That matches the prediction.

**Confirming with a debugger.** When an error message appears, a useful question is *who produced it, and what was it looking at?* gdb answers that directly:

```sh
make clox CFLAGS='-std=c99 -Isrc/clox -g -O0'   # -g: debug info, -O0: no optimising
printf '1 + 2 // a comment\n' > c.lox
gdb -q --args ./build/clox c.lox
(gdb) break errorToken          # stop whenever the scanner makes an error token
(gdb) run
(gdb) bt                        # backtrace: how did we get here?
(gdb) print *(scanner.current - 1)   # the character that was just scanned
(gdb) print scanner.line
```

Output:

```
#0  errorToken (message=0x405395 "Unexpected character.") at src/clox/scanner.c:62
#1  scanToken () at src/clox/scanner.c:241
#2  advance () at src/clox/compiler.c:74
#3  parsePrecedence (precedence=PREC_FACTOR) at src/clox/compiler.c:261
#4  binary () at src/clox/compiler.c:116
...
$2 = 10 '\n'       <- the "unexpected character" is a newline
$3 = 1             <- and we're still on line 1: case '\n' never ran
```

That's the whole story in three lines. The backtrace also shows the call chain: the parser was in `binary()` for the `+`, and asked for the next token after `2`.

### Why did it slip through?

A comment on the very last line of a file with no trailing newline works fine, because the loop stops at `'\0'` instead. And at chapter 19 you rarely write comments in one-expression test files. Bugs survive where nobody looks.

### `[M1]`: the same question in `identifierType()`

```c
case 'f':
  if (scanner.current - scanner.start > 1) {
    switch (scanner.start[1]) { ... }
    break;            // inside the if
  }
                      // a lone "f" ends up here, then falls into case 'i'
case 'i':
  return checkKeyword(1, 1, "f", TOKEN_IF);
```

For the identifier `f`, control falls into `case 'i'`, which checks whether the token is `if`. It isn't (wrong length), so it returns `TOKEN_IDENTIFIER`, which is the right answer **by accident**. The probes `f` and `fo` both behaved. It's not a bug today, but it only works because of what `case 'i'` happens to do.

### The tool that catches both: `[T3]`

After finding these by reading, I tried the compilers:

```sh
gcc   -std=c99 -Wall -Wextra                       -fsyntax-only src/clox/scanner.c   # silent
clang -std=c99 -Wall -Wextra -Wimplicit-fallthrough -fsyntax-only src/clox/scanner.c
src/clox/scanner.c:91:5: warning: unannotated fall-through between switch labels   <- [B4]
src/clox/scanner.c:127:3: warning: unannotated fall-through between switch labels  <- [M1]
```

gcc stayed quiet on this code (I didn't dig into why), while clang flagged both. **Different compilers notice different things**, so building with both now and then is cheap insurance. The devshell has both, but `make` uses gcc (`$CC`).

### Thinking about the fix

- **`[B4]`, the right fix:** add `break;` after the closing brace of the `else`, so the `for (;;)` loops and `case '\n'` handles the newline. Delete the dead `break;` after `return;` while you're there.
- **`[B4]`, tempting but wrong:** adding `case '\n':` to `scanToken()`, or calling `advance()` after the comment loop. Both treat the symptom (a stray newline reaching the scanner), and the second also skips `scanner.line++`, so every line number after a comment would be off by one. Fix the *cause*: control went to the wrong place.
- **`[M1]` fix:** move `break;` below the `if`'s closing brace.
- **How to know it worked:** the comment probe prints `3`. A two-line file with a comment on line 1 and an error on line 2 reports `[line 2]`. clang's fallthrough warning goes away.

---

## 7. Compare with the reference: `[M2]`, `[M3]`, `[M4]`

The book's finished C code is published (`c/` in the craftinginterpreters repository). It's the most reliable "supposed to", with two caveats:
- It's the code **at the end of the book**, so many functions have grown since chapter 19. Use it to check lines that should be the same, not whole files.
- The repository version has `//>` and `//<` marker comments for each chapter's snippets. Ignore them.

Comparing function by function turned up small things that aren't bugs:
- **`[M2]`** `resetStack()` in `vm.c` isn't `static`. Without `static`, the name is visible to every file linked into the program, so another file with a function of the same name would cause a link error. Default to `static` for helpers.
- **`[M3]`** `chunk.h` includes `memory.h`. The book includes it from `chunk.c`. Harmless, but generally include a header where it's *used*, so other files don't pick up dependencies they didn't ask for.
- **`[M4]`** The `OP_ADD` case in `vm.c` mixes tabs and spaces.

> **Habit:** when your code and the reference differ, ask *was this deliberate?* If yes, write a comment saying why. If you're not sure, it's probably a transcription slip.

---

## 8. The tooling around the code: `[T1]` `[T2]` `[T3]`

These aren't bugs in clox, but they shape how easy it is to find bugs.

- **`[T1]` The Makefile doesn't track header dependencies.** `src/clox/%.o: src/clox/%.c` lists only the `.c` file. If you edit `common.h` (for example to switch off `DEBUG_TRACE_EXECUTION`), `make` thinks nothing changed and keeps the old `.o` files. You end up running code that doesn't match your source, which is the worst kind of confusion. Until it's fixed, run `make clean` after touching any header. The usual fix is to add `-MMD -MP` to `CFLAGS` and `-include $(CLOX_OBJ:.o=.d)` at the end of the Makefile. gcc then writes down which headers each `.c` file used.
- **`[T2]` Keep a sanitizer build around.** They don't find anything today, but from chapter 26 (the garbage collector) on, memory bugs are the main kind of bug. ASan turns "it crashes sometimes" into "you freed this object here and used it there".
- **`[T3]` gcc and clang see different things.** Your editor's clangd uses clang, and `make` uses gcc, so the warnings can differ, as `[B4]` showed.

---

## 9. A checklist for the end of each chapter

This is everything above as a routine. Steps 1–4 take a few minutes.

1. **Clean build, warnings on:** `make clean && make clox`. Read every warning and decide whether it's intended or a bug. If it's intended, leave a comment saying so.
2. **Second opinion:** `clang -std=c99 -Wall -Wextra -Wimplicit-fallthrough -Isrc/clox -fsyntax-only src/clox/*.c`
3. **Probes:** add the new chapter's happy, edge, sad and interaction cases to a probe file, with the expected output next to each. Run the old probes too: a new chapter can break an old feature.
4. **Disassemble** any probe that involves parsing (`DEBUG_PRINT_CODE`). Check that the order of instructions matches the order you'd evaluate by hand.
5. **Sanitizer run** of all probes.
6. **"Revisit later" sweep:** search the chapter for "later", "for now" or "we'll change this", and check each spot was actually changed.
7. **Diff against the book** for the functions this chapter touched.

And for each bug you find, the loop from this walkthrough:

> **Notice** something odd → **list** the possible explanations → **predict** what a small probe will show for each → **run** it → **find** the cause with the disassembler or debugger → **fix the cause**, not the symptom → **re-run every probe**.

The book's own test suite (`tests/`) will become your main safety net once `print` arrives in chapter 21. Until then, the probes are your test suite.
