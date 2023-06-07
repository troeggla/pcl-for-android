PATCHES = ['0001-revert-cease-dependence-on-range.patch', '1.69.0-contract-no-system.patch', '1.69.0-locale-no-system.patch', '1.69.0-random-no-system.patch', '1.69.0-type_erasure-no-system.patch', '1.75.0-boost_build-with-newer-b2.patch', '1.76.0-0001-fix-include-inside-boost-namespace.patch', '1.77.0-boost_build-with-newer-b2.patch', '1.77.0-fiber-mingw.patch', '1.77.0-type_erasure-no-system.patch', '1.78.0-b2-fix-install.patch', '1.79.0-0001-json-array-erase-relocate.patch', '1.79.0-geometry_no_rtti.patch', '1.79.0-smart_ptr_cw_ppc_msync.patch', '1.80.0-0001-filesystem-win-fix-dir-it-net-share.patch', '1.80.0-0002-filesystem-fix-weakly-canonical-long-path.patch', '1.80.0-0003-unordered-valid-after-move.patch', '1.80.0-0004-filesystem-posix-fix-no-at-apis-missing-include.patch', '1.80.0-0005-config-libcpp15.patch', '1.80.0-0006-unordered-msvc-rtcc.patch', '1.80.0-locale-fail-on-missing-backend.patch', '1.81.0-locale-fail-on-missing-backend.patch', '1.82.0-locale-iconv-library-option.patch', 'bcp_namespace_issues_1_71.patch', 'bcp_namespace_issues_1_72.patch', 'boost_1_77_mpi_check.patch', 'boost_build_qcc_fix_debug_build_parameter.patch', 'boost_build_qcc_fix_debug_build_parameter_since_1_74.patch', 'boost_core_qnx_cxx_provide___cxa_get_globals.patch', 'boost_locale_fail_on_missing_backend.patch', 'boost_log_filesystem_no_deprecated_1_72.patch', 'boost_mpi_check.patch', 'python_base_prefix.patch', 'python_base_prefix_since_1_74.patch', 'solaris_pthread_data.patch']


def main():
    prefix = "https://raw.githubusercontent.com/conan-io/conan-center-index/master/recipes/boost/all/patches/"

    for patch in PATCHES:
        print(f"{prefix}{patch}")



if __name__ == "__main__":
    main()
