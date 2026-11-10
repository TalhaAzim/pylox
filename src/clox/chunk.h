#ifndef clox_chunk_h
#define clox_chunk_h

#include "common.h"
// REVIEW [M3] (minor): the book includes memory.h from chunk.c, not
// here. Include a header where it's used, so every file that includes
// chunk.h doesn't pick up memory.h (and object.h) too.
// See [M3] in CLOX_REVIEW.md and CLOX_WALKTHROUGH.md.
#include "memory.h"
#include "value.h"

typedef enum {
    OP_CONSTANT,
    OP_NIL,
    OP_TRUE,
    OP_FALSE,
    OP_EQUAL,
    OP_GREATER,
    OP_LESS,
    OP_ADD,
    OP_SUBTRACT,
    OP_MULTIPLY,
    OP_DIVIDE,
    OP_NOT,
    OP_NEGATE,
    OP_RETURN,
} OpCode;

typedef struct {
    int count;
    int capacity;
    uint8_t* code;
    int* lines;
    ValueArray constants;
} Chunk;

void initChunk(Chunk* chunk);
void freeChunk(Chunk* chunk);
void writeChunk(Chunk* chunk, uint8_t byte, int line);
int addConstant(Chunk* chunk, Value value);

#endif