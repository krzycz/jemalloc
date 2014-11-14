
Summary: A general-purpose scalable concurrent malloc(3)
Name: jemalloc
Version: 3.5.1+mk2
Release: 0
License: See COPYING
Group: System Environment/Libraries
Vendor: Intel Corporation
URL: http://github.com/memkind/jemalloc
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
%if %{defined suse_version}
BuildRequires: docbook-xsl-stylesheets
%else
BuildRequires: docbook-xsl
%endif
BuildRequires: libxslt

%description
jemalloc is a general-purpose scalable concurrent malloc(3)
implementation.  This distribution is a "portable" implementation that
currently targets FreeBSD, Linux, Apple OS X, and MinGW.  jemalloc is
included as the default allocator in the FreeBSD and NetBSD operating
systems, and it is used by the Mozilla Firefox web browser on
Microsoft Windows-related platforms.  Depending on your needs, one of
the other divergent versions may suit your needs better than this
distribution.  This package includes extensions for the memkind
library.

%prep

%setup

%package devel
Summary: A general-purpose scalable concurrent malloc(3) - development
Group: Development/Libraries

%description devel
jemalloc is a general-purpose scalable concurrent malloc(3)
implementation.  This distribution is a "portable" implementation that
currently targets FreeBSD, Linux, Apple OS X, and MinGW.  jemalloc is
included as the default allocator in the FreeBSD and NetBSD operating
systems, and it is used by the Mozilla Firefox web browser on
Microsoft Windows-related platforms.  Depending on your needs, one of
the other divergent versions may suit your needs better than this
distribution.  This package includes extensions for the memkind
library.  Package installs header files and libraries for development.

%build
%{__autoconf}
%{__mkdir_p} obj
cd obj
%if %{defined suse_version}
../configure --enable-autogen --with-jemalloc-prefix=je_ --enable-memkind --enable-safe --enable-cc-silence --prefix=%{_prefix} --includedir=%{_includedir} --libdir=%{_libdir} --bindir=%{_bindir} --docdir=%{_docdir} --mandir=%{_mandir} --with-xslroot=/usr/share/xml/docbook/stylesheet/nwalsh/current
%else
../configure --enable-autogen --with-jemalloc-prefix=je_ --enable-memkind --enable-safe --enable-cc-silence --prefix=%{_prefix} --includedir=%{_includedir} --libdir=%{_libdir} --bindir=%{_bindir} --docdir=%{_docdir} --mandir=%{_mandir}
%endif
%{__make} 
%{__make} build_doc

%install
cd obj
%{__make} DESTDIR=%{buildroot} DOCDIR=%{buildroot}/%{_docdir} install
rm -f %{buildroot}/%{_libdir}/libjemalloc.a
rm -f %{buildroot}/%{_libdir}/libjemalloc_pic.a



%clean

%post devel
/sbin/ldconfig

%postun devel
/sbin/ldconfig


%files devel
%defattr(-,root,root,-)
%{_includedir}/jemalloc
%{_includedir}/jemalloc/jemalloc.h
%{_libdir}/libjemalloc.so.1
%{_libdir}/libjemalloc.so
%{_bindir}/pprof
%{_bindir}/jemalloc.sh
%{_docdir}/jemalloc
%doc %{_docdir}/jemalloc/jemalloc.html
%doc %{_docdir}/jemalloc/README
%doc %{_docdir}/jemalloc/COPYING
%doc %{_mandir}/man3/jemalloc.3.gz


%changelog
* Thu Oct 30 2014 Christopher Cantalupo <christopher.m.cantalupo@intel.com> 3.5.1+mk2
  - Updated README with memkind information.
  - Added support for the memkind library with --enable-memkind configure
    flag.  This includes a new mallctl switch "arenas.extendk". This is a
    fork of the github jemalloc 3.5.1 release.
  - Now using weak symbols for memkind callback functions.
* Mon Feb 25 2014 Jason Evans <jasone@canonware.com> 3.5.1
- This version primarily addresses minor bugs in test code.
  Bug fixes:
- Configure Solaris/Illumos to use MADV_FREE.
- Fix junk filling for mremap(2)-based huge reallocation.  This is only
    relevant if configuring with the --enable-mremap option specified.
- Avoid compilation failure if 'restrict' C99 keyword is not supported by the
    compiler.
- Add a configure test for SSE2 rather than assuming it is usable on i686
    systems.  This fixes test compilation errors, especially on 32-bit Linux
    systems.
- Fix mallctl argument size mismatches (size_t vs. uint64_t) in the stats unit
    test.
- Fix/remove flawed alignment-related overflow tests.
- Prevent compiler optimizations that could change backtraces in the
    prof_accum unit test.
* Wed Jan 22 2014 Jason Evans <jasone@canonware.com> 3.5.0
  This version focuses on refactoring and automated testing, though it also
  includes some non-trivial heap profiling optimizations not mentioned below.
  New features:
- Add the *allocx() API, which is a successor to the experimental *allocm()
    API.  The *allocx() functions are slightly simpler to use because they have
    fewer parameters, they directly return the results of primary interest, and
    mallocx()/rallocx() avoid the strict aliasing pitfall that
    allocm()/rallocm() share with posix_memalign().  Note that *allocm() is
    slated for removal in the next non-bugfix release.
- Add support for LinuxThreads.
  Bug fixes:
- Unless heap profiling is enabled, disable floating point code and don't link
    with libm.  This, in combination with e.g. EXTRA_CFLAGS=-mno-sse on x64
    systems, makes it possible to completely disable floating point register
    use.  Some versions of glibc neglect to save/restore caller-saved floating
    point registers during dynamic lazy symbol loading, and the symbol loading
    code uses whatever malloc the application happens to have linked/loaded
    with, the result being potential floating point register corruption.
- Report ENOMEM rather than EINVAL if an OOM occurs during heap profiling
    backtrace creation in imemalign().  This bug impacted posix_memalign() and
    aligned_alloc().
- Fix a file descriptor leak in a prof_dump_maps() error path.
- Fix prof_dump() to close the dump file descriptor for all relevant error
    paths.
- Fix rallocm() to use the arena specified by the ALLOCM_ARENA(s) flag for
    allocation, not just deallocation.
- Fix a data race for large allocation stats counters.
- Fix a potential infinite loop during thread exit.  This bug occurred on
    Solaris, and could affect other platforms with similar pthreads TSD
    implementations.
- Don't junk-fill reallocations unless usable size changes.  This fixes a
    violation of the *allocx()/*allocm() semantics.
- Fix growing large reallocation to junk fill new space.
- Fix huge deallocation to junk fill when munmap is disabled.
- Change the default private namespace prefix from empty to je_, and change
    --with-private-namespace-prefix so that it prepends an additional prefix
    rather than replacing je_.  This reduces the likelihood of applications
    which statically link jemalloc experiencing symbol name collisions.
- Add missing private namespace mangling (relevant when
    --with-private-namespace is specified).
- Add and use JEMALLOC_INLINE_C so that static inline functions are marked as
    static even for debug builds.
- Add a missing mutex unlock in a malloc_init_hard() error path.  In practice
    this error path is never executed.
- Fix numerous bugs in malloc_strotumax() error handling/reporting.  These
    bugs had no impact except for malformed inputs.
- Fix numerous bugs in malloc_snprintf().  These bugs were not exercised by
    existing calls, so they had no impact.
* Sun Oct 20 2013 Jason Evans <jasone@canonware.com> 3.4.1
  Bug fixes:
- Fix a race in the "arenas.extend" mallctl that could cause memory corruption
    of internal data structures and subsequent crashes.
- Fix Valgrind integration flaws that caused Valgrind warnings about reads of
    uninitialized memory in:
    + arena chunk headers
    + internal zero-initialized data structures (relevant to tcache and prof
      code)
- Preserve errno during the first allocation.  A readlink(2) call during
    initialization fails unless /etc/malloc.conf exists, so errno was typically
    set during the first allocation prior to this fix.
- Fix compilation warnings reported by gcc 4.8.1.
* Sun Jun 2 2013 Jason Evans <jasone@canonware.com> 3.4.0
  This version is essentially a small bugfix release, but the addition of
  aarch64 support requires that the minor version be incremented.
  Bug fixes:
- Fix race-triggered deadlocks in chunk_record().  These deadlocks were
    typically triggered by multiple threads concurrently deallocating huge
    objects.
  New features:
- Add support for the aarch64 architecture.
* Wed Mar 6 2013 Jason Evans <jasone@canonware.com> 3.3.1
  This version fixes bugs that are typically encountered only when utilizing
  custom run-time options.
  Bug fixes:
- Fix a locking order bug that could cause deadlock during fork if heap
    profiling were enabled.
- Fix a chunk recycling bug that could cause the allocator to lose track of
    whether a chunk was zeroed.  On FreeBSD, NetBSD, and OS X, it could cause
    corruption if allocating via sbrk(2) (unlikely unless running with the
    "dss:primary" option specified).  This was completely harmless on Linux
    unless using mlockall(2) (and unlikely even then, unless the
    --disable-munmap configure option or the "dss:primary" option was
    specified).  This regression was introduced in 3.1.0 by the
    mlockall(2)/madvise(2) interaction fix.
- Fix TLS-related memory corruption that could occur during thread exit if the
    thread never allocated memory.  Only the quarantine and prof facilities were
    susceptible.
- Fix two quarantine bugs:
    + Internal reallocation of the quarantined object array leaked the old
      array.
    + Reallocation failure for internal reallocation of the quarantined object
      array (very unlikely) resulted in memory corruption.
- Fix Valgrind integration to annotate all internally allocated memory in a
    way that keeps Valgrind happy about internal data structure access.
- Fix building for s390 systems.
* Wed Jan 23 2013 Jason Evans <jasone@canonware.com> 3.3.0
  This version includes a few minor performance improvements in addition to the
  listed new features and bug fixes.
  New features:
- Add clipping support to lg_chunk option processing.
- Add the --enable-ivsalloc option.
- Add the --without-export option.
- Add the --disable-zone-allocator option.
  Bug fixes:
- Fix "arenas.extend" mallctl to output the number of arenas.
- Fix chunk_recycle() to unconditionally inform Valgrind that returned memory
    is undefined.
- Fix build break on FreeBSD related to alloca.h.
* Fri Nov 9 2012 Jason Evans <jasone@canonware.com> 3.2.0
  In addition to a couple of bug fixes, this version modifies page run
  allocation and dirty page purging algorithms in order to better control
  page-level virtual memory fragmentation.
  Incompatible changes:
- Change the "opt.lg_dirty_mult" default from 5 to 3 (32:1 to 8:1).
  Bug fixes:
- Fix dss/mmap allocation precedence code to use recyclable mmap memory only
    after primary dss allocation fails.
- Fix deadlock in the "arenas.purge" mallctl.  This regression was introduced
    in 3.1.0 by the addition of the "arena.<i>.purge" mallctl.
* Tue Oct 16 2012 Jason Evans <jasone@canonware.com> 3.1.0
  New features:
- Auto-detect whether running inside Valgrind, thus removing the need to
    manually specify MALLOC_CONF=valgrind:true.
- Add the "arenas.extend" mallctl, which allows applications to create
    manually managed arenas.
- Add the ALLOCM_ARENA() flag for {,r,d}allocm().
- Add the "opt.dss", "arena.<i>.dss", and "stats.arenas.<i>.dss" mallctls,
    which provide control over dss/mmap precedence.
- Add the "arena.<i>.purge" mallctl, which obsoletes "arenas.purge".
- Define LG_QUANTUM for hppa.
  Incompatible changes:
- Disable tcache by default if running inside Valgrind, in order to avoid
    making unallocated objects appear reachable to Valgrind.
- Drop const from malloc_usable_size() argument on Linux.
  Bug fixes:
- Fix heap profiling crash if sampled object is freed via realloc(p, 0).
- Remove const from __*_hook variable declarations, so that glibc can modify
    them during process forking.
- Fix mlockall(2)/madvise(2) interaction.
- Fix fork(2)-related deadlocks.
- Fix error return value for "thread.tcache.enabled" mallctl.
* Fri May 11 2012 Jason Evans <jasone@canonware.com> 3.0.0
  Although this version adds some major new features, the primary focus is on
  internal code cleanup that facilitates maintainability and portability, most
  of which is not reflected in the ChangeLog.  This is the first release to
  incorporate substantial contributions from numerous other developers, and the
  result is a more broadly useful allocator (see the git revision history for
  contribution details).  Note that the license has been unified, thanks to
  Facebook granting a license under the same terms as the other copyright
  holders (see COPYING).
  New features:
- Implement Valgrind support, redzones, and quarantine.
- Add support for additional platforms:
    + FreeBSD
    + Mac OS X Lion
    + MinGW
    + Windows (no support yet for replacing the system malloc)
- Add support for additional architectures:
    + MIPS
    + SH4
    + Tilera
- Add support for cross compiling.
- Add nallocm(), which rounds a request size up to the nearest size class
    without actually allocating.
- Implement aligned_alloc() (blame C11).
- Add the "thread.tcache.enabled" mallctl.
- Add the "opt.prof_final" mallctl.
- Update pprof (from gperftools 2.0).
- Add the --with-mangling option.
- Add the --disable-experimental option.
- Add the --disable-munmap option, and make it the default on Linux.
- Add the --enable-mremap option, which disables use of mremap(2) by default.
  Incompatible changes:
- Enable stats by default.
- Enable fill by default.
- Disable lazy locking by default.
- Rename the "tcache.flush" mallctl to "thread.tcache.flush".
- Rename the "arenas.pagesize" mallctl to "arenas.page".
- Change the "opt.lg_prof_sample" default from 0 to 19 (1 B to 512 KiB).
- Change the "opt.prof_accum" default from true to false.
  Removed features:
- Remove the swap feature, including the "config.swap", "swap.avail",
    "swap.prezeroed", "swap.nfds", and "swap.fds" mallctls.
- Remove highruns statistics, including the
    "stats.arenas.<i>.bins.<j>.highruns" and
    "stats.arenas.<i>.lruns.<j>.highruns" mallctls.
- As part of small size class refactoring, remove the "opt.lg_[qc]space_max",
    "arenas.cacheline", "arenas.subpage", "arenas.[tqcs]space_{min,max}", and
    "arenas.[tqcs]bins" mallctls.
- Remove the "arenas.chunksize" mallctl.
- Remove the "opt.lg_prof_tcmax" option.
- Remove the "opt.lg_prof_bt_max" option.
- Remove the "opt.lg_tcache_gc_sweep" option.
- Remove the --disable-tiny option, including the "config.tiny" mallctl.
- Remove the --enable-dynamic-page-shift configure option.
- Remove the --enable-sysv configure option.
  Bug fixes:
- Fix a statistics-related bug in the "thread.arena" mallctl that could cause
    invalid statistics and crashes.
- Work around TLS deallocation via free() on Linux.  This bug could cause
    write-after-free memory corruption.
- Fix a potential deadlock that could occur during interval- and
    growth-triggered heap profile dumps.
- Fix large calloc() zeroing bugs due to dropping chunk map unzeroed flags.
- Fix chunk_alloc_dss() to stop claiming memory is zeroed.  This bug could
    cause memory corruption and crashes with --enable-dss specified.
- Fix fork-related bugs that could cause deadlock in children between fork
    and exec.
- Fix malloc_stats_print() to honor 'b' and 'l' in the opts parameter.
- Fix realloc(p, 0) to act like free(p).
- Do not enforce minimum alignment in memalign().
- Check for NULL pointer in malloc_usable_size().
- Fix an off-by-one heap profile statistics bug that could be observed in
    interval- and growth-triggered heap profiles.
- Fix the "epoch" mallctl to update cached stats even if the passed in epoch
    is 0.
- Fix bin->runcur management to fix a layout policy bug.  This bug did not
    affect correctness.
- Fix a bug in choose_arena_hard() that potentially caused more arenas to be
    initialized than necessary.
- Add missing "opt.lg_tcache_max" mallctl implementation.
- Use glibc allocator hooks to make mixed allocator usage less likely.
- Fix build issues for --disable-tcache.
- Don't mangle pthread_create() when --with-private-namespace is specified.
* Mon Nov 14 2011 Jason Evans <jasone@canonware.com> 2.2.5
  Bug fixes:
- Fix huge_ralloc() race when using mremap(2).  This is a serious bug that
    could cause memory corruption and/or crashes.
- Fix huge_ralloc() to maintain chunk statistics.
- Fix malloc_stats_print(..., "a") output.
* Sat Nov 5 2011 Jason Evans <jasone@canonware.com> 2.2.4
  Bug fixes:
- Initialize arenas_tsd before using it.  This bug existed for 2.2.[0-3], as
    well as for --disable-tls builds in earlier releases.
- Do not assume a 4 KiB page size in test/rallocm.c.
* Wed Aug 31 2011 Jason Evans <jasone@canonware.com> 2.2.3
  This version fixes numerous bugs related to heap profiling.
  Bug fixes:
- Fix a prof-related race condition.  This bug could cause memory corruption,
    but only occurred in non-default configurations (prof_accum:false).
- Fix off-by-one backtracing issues (make sure that prof_alloc_prep() is
    excluded from backtraces).
- Fix a prof-related bug in realloc() (only triggered by OOM errors).
- Fix prof-related bugs in allocm() and rallocm().
- Fix prof_tdata_cleanup() for --disable-tls builds.
- Fix a relative include path, to fix objdir builds.
* Sat Jul 30 2011 Jason Evans <jasone@canonware.com> 2.2.2
  Bug fixes:
- Fix a build error for --disable-tcache.
- Fix assertions in arena_purge() (for real this time).
- Add the --with-private-namespace option.  This is a workaround for symbol
    conflicts that can inadvertently arise when using static libraries.
* Wed Mar 30 2011 Jason Evans <jasone@canonware.com> 2.2.1
  Bug fixes:
- Implement atomic operations for x86/x64.  This fixes compilation failures
    for versions of gcc that are still in wide use.
- Fix an assertion in arena_purge().
* Tue Mar 22 2011 Jason Evans <jasone@canonware.com> 2.2.0
  This version incorporates several improvements to algorithms and data
  structures that tend to reduce fragmentation and increase speed.
  New features:
- Add the "stats.cactive" mallctl.
- Update pprof (from google-perftools 1.7).
- Improve backtracing-related configuration logic, and add the
    --disable-prof-libgcc option.
  Bug fixes:
- Change default symbol visibility from "internal", to "hidden", which
    decreases the overhead of library-internal function calls.
- Fix symbol visibility so that it is also set on OS X.
- Fix a build dependency regression caused by the introduction of the .pic.o
    suffix for PIC object files.
- Add missing checks for mutex initialization failures.
- Don't use libgcc-based backtracing except on x64, where it is known to work.
- Fix deadlocks on OS X that were due to memory allocation in
    pthread_mutex_lock().
- Heap profiling-specific fixes:
    + Fix memory corruption due to integer overflow in small region index
      computation, when using a small enough sample interval that profiling
      context pointers are stored in small run headers.
    + Fix a bootstrap ordering bug that only occurred with TLS disabled.
    + Fix a rallocm() rsize bug.
    + Fix error detection bugs for aligned memory allocation.
* Mon Mar 14 2011 Jason Evans <jasone@canonware.com> 2.1.3
  Bug fixes:
- Fix a cpp logic regression (due to the "thread.{de,}allocatedp" mallctl fix
    for OS X in 2.1.2).
- Fix a "thread.arena" mallctl bug.
- Fix a thread cache stats merging bug.
* Wed Mar 2 2011 Jason Evans <jasone@canonware.com> 2.1.2
  Bug fixes:
- Fix "thread.{de,}allocatedp" mallctl for OS X.
- Add missing jemalloc.a to build system.
* Mon Jan 31 2011 Jason Evans <jasone@canonware.com> 2.1.1
  Bug fixes:
- Fix aligned huge reallocation (affected allocm()).
- Fix the ALLOCM_LG_ALIGN macro definition.
- Fix a heap dumping deadlock.
- Fix a "thread.arena" mallctl bug.
* Fri Dec 3 2010 Jason Evans <jasone@canonware.com> 2.1.0
  This version incorporates some optimizations that can't quite be considered
  bug fixes.
  New features:
- Use Linux's mremap(2) for huge object reallocation when possible.
- Avoid locking in mallctl*() when possible.
- Add the "thread.[de]allocatedp" mallctl's.
- Convert the manual page source from roff to DocBook, and generate both roff
    and HTML manuals.
  Bug fixes:
- Fix a crash due to incorrect bootstrap ordering.  This only impacted
    --enable-debug --enable-dss configurations.
- Fix a minor statistics bug for mallctl("swap.avail", ...).
* Fri Oct 29 2010 Jason Evans <jasone@canonware.com> 2.0.1
  Bug fixes:
- Fix a race condition in heap profiling that could cause undefined behavior
    if "opt.prof_accum" were disabled.
- Add missing mutex unlocks for some OOM error paths in the heap profiling
    code.
- Fix a compilation error for non-C99 builds.
* Sun Oct 24 2010 Jason Evans <jasone@canonware.com> 2.0.0
  This version focuses on the experimental *allocm() API, and on improved
  run-time configuration/introspection.  Nonetheless, numerous performance
  improvements are also included.
  New features:
- Implement the experimental {,r,s,d}allocm() API, which provides a superset
    of the functionality available via malloc(), calloc(), posix_memalign(),
    realloc(), malloc_usable_size(), and free().  These functions can be used to
    allocate/reallocate aligned zeroed memory, ask for optional extra memory
    during reallocation, prevent object movement during reallocation, etc.
- Replace JEMALLOC_OPTIONS/JEMALLOC_PROF_PREFIX with MALLOC_CONF, which is
    more human-readable, and more flexible.  For example:
      JEMALLOC_OPTIONS=AJP
    is now:
      MALLOC_CONF=abort:true,fill:true,stats_print:true
- Port to Apple OS X.  Sponsored by Mozilla.
- Make it possible for the application to control thread-->arena mappings via
    the "thread.arena" mallctl.
- Add compile-time support for all TLS-related functionality via pthreads TSD.
    This is mainly of interest for OS X, which does not support TLS, but has a
    TSD implementation with similar performance.
- Override memalign() and valloc() if they are provided by the system.
- Add the "arenas.purge" mallctl, which can be used to synchronously purge all
    dirty unused pages.
- Make cumulative heap profiling data optional, so that it is possible to
    limit the amount of memory consumed by heap profiling data structures.
- Add per thread allocation counters that can be accessed via the
    "thread.allocated" and "thread.deallocated" mallctls.
  Incompatible changes:
- Remove JEMALLOC_OPTIONS and malloc_options (see MALLOC_CONF above).
- Increase default backtrace depth from 4 to 128 for heap profiling.
- Disable interval-based profile dumps by default.
  Bug fixes:
- Remove bad assertions in fork handler functions.  These assertions could
    cause aborts for some combinations of configure settings.
- Fix strerror_r() usage to deal with non-standard semantics in GNU libc.
- Fix leak context reporting.  This bug tended to cause the number of contexts
    to be underreported (though the reported number of objects and bytes were
    correct).
- Fix a realloc() bug for large in-place growing reallocation.  This bug could
    cause memory corruption, but it was hard to trigger.
- Fix an allocation bug for small allocations that could be triggered if
    multiple threads raced to create a new run of backing pages.
- Enhance the heap profiler to trigger samples based on usable size, rather
    than request size.
- Fix a heap profiling bug due to sometimes losing track of requested object
    size for sampled objects.
* Thu Aug 12 2010 Jason Evans <jasone@canonware.com> 1.0.3
  Bug fixes:
- Fix the libunwind-based implementation of stack backtracing (used for heap
    profiling).  This bug could cause zero-length backtraces to be reported.
- Add a missing mutex unlock in library initialization code.  If multiple
    threads raced to initialize malloc, some of them could end up permanently
    blocked.
* Tue May 11 2010 Jason Evans <jasone@canonware.com> 1.0.2
  Bug fixes:
- Fix junk filling of large objects, which could cause memory corruption.
- Add MAP_NORESERVE support for chunk mapping, because otherwise virtual
    memory limits could cause swap file configuration to fail.  Contributed by
    Jordan DeLong.
* Wed Apr 14 2010 Jason Evans <jasone@canonware.com> 1.0.1
  Bug fixes:
- Fix compilation when --enable-fill is specified.
- Fix threads-related profiling bugs that affected accuracy and caused memory
    to be leaked during thread exit.
- Fix dirty page purging race conditions that could cause crashes.
- Fix crash in tcache flushing code during thread destruction.
* Sun Apr 11 2010 Jason Evans <jasone@canonware.com> 1.0.0
  This release focuses on speed and run-time introspection.  Numerous
  algorithmic improvements make this release substantially faster than its
  predecessors.
  New features:
- Implement autoconf-based configuration system.
- Add mallctl*(), for the purposes of introspection and run-time
    configuration.
- Make it possible for the application to manually flush a thread's cache, via
    the "tcache.flush" mallctl.
- Base maximum dirty page count on proportion of active memory.
- Compute various addtional run-time statistics, including per size class
    statistics for large objects.
- Expose malloc_stats_print(), which can be called repeatedly by the
    application.
- Simplify the malloc_message() signature to only take one string argument,
    and incorporate an opaque data pointer argument for use by the application
    in combination with malloc_stats_print().
- Add support for allocation backed by one or more swap files, and allow the
    application to disable over-commit if swap files are in use.
- Implement allocation profiling and leak checking.
  Removed features:
- Remove the dynamic arena rebalancing code, since thread-specific caching
    reduces its utility.
  Bug fixes:
- Modify chunk allocation to work when address space layout randomization
    (ASLR) is in use.
- Fix thread cleanup bugs related to TLS destruction.
- Handle 0-size allocation requests in posix_memalign().
- Fix a chunk leak.  The leaked chunks were never touched, so this impacted
    virtual memory usage, but not physical memory usage.
* Wed Aug 27 2008 Jason Evans <jasone@canonware.com> linux_2008082[78]a
  These snapshot releases are the simple result of incorporating Linux-specific
  support into the FreeBSD malloc sources.

