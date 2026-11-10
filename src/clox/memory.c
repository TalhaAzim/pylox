#include <stdlib.h>

#include "memory.h"
#include "vm.h"

void* reallocate(void* pointer, size_t oldSize, size_t newSize) {
    if (newSize == 0) {
        free(pointer);
        return NULL;
    }

    void* result = realloc(pointer, newSize);
    if (result == NULL) exit(1);
    return result;
}

// REVIEW [B1] (the build fails here). freeObjects() calls freeObject(),
// but freeObject() is only defined further down the file. C reads a file
// top to bottom, so at the call the compiler has never seen freeObject.
// C99 guesses an "implicit declaration" for it (non-static, returning int).
// Then the real definition below says `static void`, which contradicts the
// guess, and gcc stops:
//   error: static declaration of 'freeObject' follows non-static declaration
// How to spot it: "implicit declaration of function" always means "used
// before it was declared". A static helper has to sit above its callers
// (the book puts freeObject() first) or be forward-declared near the top:
//   static void freeObject(Obj* object);
// See [B1] in CLOX_REVIEW.md and CLOX_WALKTHROUGH.md.
void freeObjects() {
  Obj *object = vm.objects;
  while (object != NULL) {
    Obj *next = object->next;
    freeObject(object);
    object = next;
  }
}

static void freeObject(Obj *object) {
  switch (object->type) {
  case OBJ_STRING: {
    ObjString *string = (ObjString *)object;
    FREE_ARRAY(char, string->chars, string->length + 1);
    FREE(ObjString, object);
    break;
  }
  }
}
