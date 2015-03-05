#include "test/jemalloc_test.h"

chunk_alloc_t *old_alloc;
chunk_dalloc_t *old_dalloc;

bool
chunk_dalloc(void *chunk, size_t size, unsigned arena_ind)
{

	return (old_dalloc(chunk, size, arena_ind));
}

void *
chunk_alloc(void *new_addr, size_t size, size_t alignment, bool *zero,
    unsigned arena_ind)
{

	return (old_alloc(new_addr, size, alignment, zero, arena_ind));
}

chunk_mmap_t *old_mmap;
chunk_munmap_t *old_munmap;

void *
chunk_mmap(size_t size, size_t alignment, bool *zero)
{

	return (old_mmap(size, alignment, zero));
}

bool
chunk_munmap(void *chunk, size_t size)
{

	return (old_munmap(chunk, size));
}


TEST_BEGIN(test_chunk)
{
	void *p;
	chunk_alloc_t *new_alloc;
	chunk_dalloc_t *new_dalloc;
	size_t old_size, new_size;

	new_alloc = chunk_alloc;
	new_dalloc = chunk_dalloc;
	old_size = sizeof(chunk_alloc_t *);
	new_size = sizeof(chunk_alloc_t *);

	assert_d_eq(mallctl("arena.0.chunk.alloc", &old_alloc,
	    &old_size, &new_alloc, new_size), 0,
	    "Unexpected alloc error");
	assert_ptr_ne(old_alloc, new_alloc,
	    "Unexpected alloc error");
	assert_d_eq(mallctl("arena.0.chunk.dalloc", &old_dalloc, &old_size,
	    &new_dalloc, new_size), 0, "Unexpected dalloc error");
	assert_ptr_ne(old_dalloc, new_dalloc, "Unexpected dalloc error");

	p = mallocx(42, 0);
	assert_ptr_ne(p, NULL, "Unexpected alloc error");
	free(p);

	assert_d_eq(mallctl("arena.0.chunk.alloc", NULL,
	    NULL, &old_alloc, old_size), 0,
	    "Unexpected alloc error");
	assert_d_eq(mallctl("arena.0.chunk.dalloc", NULL, NULL, &old_dalloc,
	    old_size), 0, "Unexpected dalloc error");
}
TEST_END


TEST_BEGIN(test_chunk_mmap)
{
	void *p;
	chunk_mmap_t *new_mmap;
	chunk_munmap_t *new_munmap;
	size_t old_size, new_size;

	new_mmap = chunk_mmap;
	new_munmap = chunk_munmap;
	old_size = sizeof(chunk_mmap_t *);
	new_size = sizeof(chunk_munmap_t *);

	assert_d_eq(mallctl("arena.0.chunk.mmap", &old_mmap,
	    &old_size, &new_mmap, new_size), 0,
	    "Unexpected mmap error");
	assert_ptr_ne(old_mmap, new_mmap,
	    "Unexpected mmap error");
	assert_d_eq(mallctl("arena.0.chunk.munmap", &old_munmap, &old_size,
	    &new_munmap, new_size), 0, "Unexpected munmap error");
	assert_ptr_ne(old_munmap, new_munmap, "Unexpected munmap error");

	p = mallocx(42, 0);
	assert_ptr_ne(p, NULL, "Unexpected mmap error");
	free(p);

	assert_d_eq(mallctl("arena.0.chunk.mmap", NULL,
	    NULL, &old_mmap, old_size), 0,
	    "Unexpected mmap error");
	assert_d_eq(mallctl("arena.0.chunk.munmap", NULL, NULL, &old_munmap,
	    old_size), 0, "Unexpected munmap error");
}
TEST_END

int
main(void)
{

	return (test(
	    test_chunk,
	    test_chunk_mmap));
}
