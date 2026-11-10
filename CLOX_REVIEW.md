# clox review (issue #1)

Review of `reference-clox` at `1e199fc`, the end of chapter 19 (Strings). Nothing in this branch is fixed. Each finding has a tag (`[B1]`–`[B4]` bugs, `[M1]`–`[M4]` minor, `[T1]`–`[T3]` tooling). The same tag marks the `// REVIEW` comment at the line in the source, and the part of `CLOX_WALKTHROUGH.md` that describes how it was found, tested and fixed. Search for a tag to move between the three.

Every bug was confirmed on cairo by building a scratch copy with only bug 1 patched, so it would compile.

| # | Where | Symptom | Would a tool have caught it? |
|---|-------|---------|------------------------------|
| B1 | `memory.c`, `freeObjects()` | The build fails | Yes: compile error |
| B2 | `compiler.c`, `consume()` | Syntax errors are silently ignored | Yes: `-Wunused-parameter` (already on, via `-Wextra`) |
| B3 | `compiler.c`, `unary()` | `-1 + 2` prints `-3` | No: only testing catches it |
| B4 | `scanner.c`, `skipWhiteSpace()` | Any `//` comment before a newline is an error | Yes: clang `-Wimplicit-fallthrough` |

## The bugs

### [B1] `freeObject()` is used before it's declared (memory.c)

`freeObjects()` calls `freeObject()`, but `freeObject()` is defined lower in the file as `static void`. At the call, the compiler has never seen it. C99 makes up an implicit declaration (non-static, returning `int`), and the real definition then conflicts with that guess:

```
error: implicit declaration of function 'freeObject'
error: static declaration of 'freeObject' follows non-static declaration
```

**What to remember:** "implicit declaration" always means "used before declared". Put static helpers above their callers, or forward-declare them.

### [B2] `consume()` never reports an error (compiler.c)

The last line, `errorAtCurrent(message);`, is missing. When the expected token isn't there, `consume()` just returns and nobody hears about it:

| Input | Got | Expected |
|-------|-----|----------|
| `(1 + 2` | prints `3`, exit 0 | `Expect ')' after expression.`, exit 65 |
| `1 2` | prints `1`, exit 0 | `Expect end of expression.`, exit 65 |

**What to remember:** the build was already warning `unused parameter 'message'`. An unused parameter often means a missing line. It's worth treating every warning as a question rather than noise.

### [B3] Unary operand parsed at the wrong precedence (compiler.c)

`unary()` calls `expression()` for its operand. The book uses `expression()` as a placeholder in 17.4, then changes it to `parsePrecedence(PREC_UNARY)` in 17.6.1. That second change was missed. `expression()` parses at the lowest precedence, so the operand swallows the rest of the expression:

| Input | Parsed as | Got | Expected |
|-------|-----------|-----|----------|
| `-1 + 2` | `-(1 + 2)` | `-3` | `1` |
| `-2 * 3 + 1` | `-(2 * 3 + 1)` | `-7` | `-5` |
| `!nil == false` | `!(nil == false)` | `true` | `false` |

**What to remember:** no compiler catches a logic bug like this. Test it with an expression where the grouping changes the answer, and work out the expected result by hand first. Watch out for tests that pass either way: for booleans, `!(a == b)` always equals `(!a) == b`, so `!true == false` can't reveal this bug.

When the book says "we'll come back and change this later", leave yourself a `// TODO` there.

### [B4] Missing `break` after skipping a comment (scanner.c)

In `skipWhiteSpace()`, the `case '/'` branch has no `break;` after its `if/else`. C switch cases fall through, so after skipping a comment, control falls into `default: return;`. The function returns while still sitting on the `\n` that ended the comment. `scanToken()` then tries to scan `\n` as a token and reports `Unexpected character.`

```
1 + 2 // a comment
```
→ `[line 1] Error: Unexpected character.` (A comment on the last line of a file with no trailing newline works, which is why this is easy to miss.)

**What to remember:** for every `case`, ask where control goes when it ends. clang has a warning for this; gcc's `-Wall -Wextra` didn't report it:

```
clang -std=c99 -Wall -Wextra -Wimplicit-fallthrough -Isrc/clox -fsyntax-only src/clox/*.c
```

## Minor: not bugs today

- **[M1] scanner.c, `identifierType()`, `case 'f'`:** the `break;` is inside the `if`, so a lone `f` falls through into `case 'i'`. It returns `TOKEN_IDENTIFIER` anyway, but only by luck. clang's fallthrough warning flags this one too.
- **[M2] vm.c, `resetStack()`:** not `static` (it is in the book). Make file-local helpers `static` so they can't clash with names in other files.
- **[M3] chunk.h** includes `memory.h`. The book includes it from `chunk.c` instead. This is harmless.
- **[M4] vm.c, the `OP_ADD` branch,** is indented with tabs, while the rest of the file uses spaces.

## Tooling

- **[T1] The Makefile doesn't track headers.** After editing a `.h` file, such as toggling `DEBUG_TRACE_EXECUTION` in `common.h`, `make clox` won't rebuild the `.o` files that depend on it until you run `make clean`. That can make it look like a change "didn't work". Adding `-MMD -MP` to `CFLAGS` and `-include $(CLOX_OBJ:.o=.d)` fixes it.
- **[T2] Sanitizers find memory bugs while you test.** Compiling with `-g -fsanitize=address,undefined` reports leaks, use-after-free and out-of-bounds access as soon as they happen. These will matter more once the garbage collector arrives (chapter 26). With bug 1 patched, the current code ran clean under them.
- **[T3] `$CC` in the devshell is gcc,** even though clang is installed, while `make compile_commands` (used by clangd in the editor) writes clang commands. So the editor and the build can show different warnings, as with bug 4.

## Also noticed: pylox tests

`make test` runs pylox, not clox. Six tests crash with a Python traceback instead of a Lox error:

- `limit/stack_overflow.lox`: the handler reads `.message`, which Python's `RecursionError` doesn't have.
- `number/nan_equality.lox`: Python raises `ZeroDivisionError` on `0/0`, where Lox expects NaN.
- `operator/{multiply,divide}_{num_nonnum,nonnum_num}.lox`: a raw Python `TypeError` instead of "Operands must be numbers."

`make test` never fails on them, because `find -exec` discards each test's exit code.
