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


void *
chunk_mmap1(size_t size, size_t alignment, bool *zero)
{
	void *ptr = old_mmap(size, alignment, zero);
	memset(ptr, 1, size);
	return ptr;
}

bool
chunk_munmap1(void *chunk, size_t size)
{
	assert_d_eq(*(char *)chunk, 1,
		    "Error in munmap1");
	return (old_munmap(chunk, size));
}

void *
chunk_mmap2(size_t size, size_t alignment, bool *zero)
{
	void *ptr = old_mmap(size, alignment, zero);
	memset(ptr, 2, size);
	return ptr;
}

bool
chunk_munmap2(void *chunk, size_t size)
{
	assert_d_eq(*(char *)chunk, 2,
		    "Error in munmap2");
	return (old_munmap(chunk, size));
}


TEST_BEGIN(test_chunk_mmap_arena)
{
	void *p0;
	void *p1;
	void *p2;
	chunk_mmap_t *new_mmap;
	chunk_munmap_t *new_munmap;
	size_t old_size, new_size;

	size_t mib[4];
	size_t miblen = sizeof(mib) / sizeof(size_t);

	unsigned arena1;
	unsigned arena2;
	size_t sz;

	p0 = mallocx(8*1024*1024, 0);

	sz = sizeof(arena1);
	assert_d_eq(mallctl("arenas.extend", &arena1, &sz, NULL, 0), 0,
	    "Error in arenas.extend");

	sz = sizeof(arena2);
	assert_d_eq(mallctl("arenas.extend", &arena2, &sz, NULL, 0), 0,
	    "Error in arenas.extend");

	old_size = sizeof(chunk_mmap_t *);
	new_size = sizeof(chunk_munmap_t *);

	new_mmap = chunk_mmap1;
	new_munmap = chunk_munmap1;

	assert_d_eq(mallctlnametomib("arena.0.chunk.mmap", mib, &miblen), 0,
	    "Error in mallctlnametomib()");
	mib[1] = arena1;
	assert_d_eq(mallctlbymib(mib, miblen, &old_mmap, &old_size,
	    &new_mmap, new_size), 0,
	    "Error in mallctlbymib()");

	assert_d_eq(mallctlnametomib("arena.0.chunk.munmap", mib, &miblen), 0,
	    "Error in mallctlnametomib()");
	mib[1] = arena1;
	assert_d_eq(mallctlbymib(mib, miblen, &old_munmap, &old_size,
	    &new_munmap, new_size), 0,
	    "Error in mallctlbymib()");

	new_mmap = chunk_mmap2;
	new_munmap = chunk_munmap2;

	assert_d_eq(mallctlnametomib("arena.0.chunk.mmap", mib, &miblen), 0,
	    "Error in mallctlnametomib()");
	mib[1] = arena2;
	assert_d_eq(mallctlbymib(mib, miblen, &old_mmap, &old_size,
	    &new_mmap, new_size), 0,
	    "Error in mallctlbymib()");

	assert_d_eq(mallctlnametomib("arena.0.chunk.munmap", mib, &miblen), 0,
	    "Error in mallctlnametomib()");
	mib[1] = arena2;
	assert_d_eq(mallctlbymib(mib, miblen, &old_munmap, &old_size,
	    &new_munmap, new_size), 0,
	    "Error in mallctlbymib()");

	p1 = mallocx(8*1024*1024, MALLOCX_ARENA(arena1));
	assert_ptr_ne(p1, NULL, "Unexpected mmap error");
	assert_d_eq(*(char *)p1, 1, "Unexpected value");

	p2 = mallocx(4*1024*1024, MALLOCX_ARENA(arena2));
	assert_ptr_ne(p2, NULL, "Unexpected mmap error");
	assert_d_eq(*(char *)p2, 2, "Unexpected value");

	free(p1);
	free(p2);

	p2 = mallocx(8*1024*1024, MALLOCX_ARENA(arena2));
	assert_ptr_ne(p2, NULL, "Unexpected mmap error");
	assert_d_eq(*(char *)p2, 2, "Unexpected value");

	free(p2);

	free(p0);
}
TEST_END


int
main(void)
{

	return (test(
	    test_chunk,
	    test_chunk_mmap,
	    test_chunk_mmap_arena));
}
