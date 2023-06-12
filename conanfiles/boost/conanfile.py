from conan import ConanFile, tools
from os import path

import yaml


class BoostConan(ConanFile):
    name = "boost"
    version = "1.76.0"
    settings = "os", "compiler", "arch", "build_type"
    description = "Conan package for boost library"
    url = "https://www.boost.org/"
    license = "Boost Software License"
    folder_name = "boost_{}".format(version.replace(".", "_"))
    user = "pcl-android"
    channel = "stable"
    options = {
        "shared": [True, False],
    }
    default_options = {
        "shared": False,
    }

    _cached_dependencies = None

    def export(self):
        tools.files.copy(self, f"dependencies/{self._dependency_filename}", src=self.recipe_folder, dst=self.export_folder)

    @property
    def _dependency_filename(self):
        return f"dependencies-{self.version}.yml"

    @property
    def _dependencies(self):
        if self._cached_dependencies is None:
            dependencies_filepath = path.join(self.recipe_folder, "dependencies", self._dependency_filename)

            if not path.isfile(dependencies_filepath):
                raise FileNotFoundError(f"Cannot find {dependencies_filepath}")

            with open(dependencies_filepath, encoding='utf-8') as f:
                self._cached_dependencies = yaml.safe_load(f)

        return self._cached_dependencies

    def _to_android_arch(self, arch: str) -> str:
        if arch == "armv7":
            return "armv7a"
        if arch == "armv8":
            return "aarch64"
        if arch == "x86":
            return "i686"

        return arch

    def _to_build_os(self, os: str) -> str:
        if os == "Linux":
            return "linux"
        elif os == "Macos":
            return "darwin"

        return os

    def _to_android_address_model(self, arch: str) -> str:
        if arch == "armv8" or arch == "x86_64":
            return "64"

        return "32"

    def _to_boost_arch(self, arch: str) -> str:
        if arch.startswith("arm") or arch == "aarch64":
            return "arm"

        return "x86"

    def _configure_user_config(self) -> None:
        if str(self.settings.arch) == "armv7":
            ext = "eabi"
        else:
            ext = ""

        ndk_path = self.conf.get("tools.android:ndk_path")
        path_to_clang_compiler = "{}/toolchains/llvm/prebuilt/{}-x86_64/bin/{}-linux-android{}{}-clang++".format(
            ndk_path,
            self._to_build_os(self.settings_build.os),
            self._to_android_arch(str(self.settings.arch)),
            ext,
            self.settings.os.api_level
        )

        print("Compiler: {}".format(path_to_clang_compiler))

        compiler_flags = "-fPIC -std=c++14 -stdlib=libc++"
        user_config = "using clang : androidos : {}\n: <cxxflags>\"{}\"\n;".format(path_to_clang_compiler, compiler_flags)
        path_to_user_config = "{}/{}/tools/build/src/user-config.jam".format(self.build_folder, self.folder_name)

        file = open(path_to_user_config, "w")
        file.write(user_config)
        file.close()

    def _configure_boost(self) -> None:
        self.run("./bootstrap.sh")

    def _build_boost(self) -> None:
        b2_comd = "./b2 link={} variant=release threading=multi --without-python --debug-configuration --abbreviate-paths architecture={} --stagedir={} target-os=android address-model={} abi=aapcs".format(
            "shared" if self.options.shared else "static",
            self._to_boost_arch(str(self.settings.arch)),
            self.settings.arch,
            self._to_android_address_model(str(self.settings.arch))
        )

        self.run(b2_comd)

    def source(self):
        tools.files.get(self, "https://boostorg.jfrog.io/artifactory/main/release/{}/source/{}.tar.gz".format(self.version, self.folder_name))

    def build(self):
        with tools.files.chdir(self, self.folder_name):
            self._configure_user_config()
            self._configure_boost()
            self._build_boost()

    def package(self):
        tools.files.copy(self, pattern="*.a", dst=path.join(self.package_folder, "lib"), src="{}/{}/lib".format(self.folder_name, self.settings.arch))
        tools.files.copy(self, pattern="*.so", dst=path.join(self.package_folder, "lib"), src="{}/{}/lib".format(self.folder_name, self.settings.arch))
        tools.files.copy(self, pattern="*.so." + self.version, dst=path.join(self.package_folder, "lib"), src="{}/{}/lib".format(self.folder_name, self.settings.arch))
        tools.files.copy(self, pattern="*", dst=path.join(self.package_folder , "include/boost"), src="{}/boost".format(self.folder_name))

    def package_info(self):
        self.env_info.BOOST_ROOT = self.package_folder

        self.cpp_info.set_property("cmake_file_name", "Boost")
        self.cpp_info.filenames["cmake_find_package"] = "Boost"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Boost"
        self.cpp_info.names["cmake_find_package"] = "Boost"
        self.cpp_info.names["cmake_find_package_multi"] = "Boost"

        # - Use 'headers' component for all includes + defines
        # - Use '_libboost' component to attach extra system_libs, ...

        self.cpp_info.components["headers"].libs = []
        self.cpp_info.components["headers"].set_property("cmake_target_name", "Boost::headers")
        self.cpp_info.components["headers"].names["cmake_find_package"] = "headers"
        self.cpp_info.components["headers"].names["cmake_find_package_multi"] = "headers"
        self.cpp_info.components["headers"].names["pkg_config"] = "boost"

        # Boost::boost is an alias of Boost::headers
        self.cpp_info.components["_boost_cmake"].requires = ["headers"]
        self.cpp_info.components["_boost_cmake"].set_property("cmake_target_name", "Boost::boost")
        self.cpp_info.components["_boost_cmake"].names["cmake_find_package"] = "boost"
        self.cpp_info.components["_boost_cmake"].names["cmake_find_package_multi"] = "boost"

        self.cpp_info.components["_libboost"].requires = ["headers"]

        self.cpp_info.components["diagnostic_definitions"].libs = []
        self.cpp_info.components["diagnostic_definitions"].set_property("cmake_target_name", "Boost::diagnostic_definitions")
        self.cpp_info.components["diagnostic_definitions"].names["cmake_find_package"] = "diagnostic_definitions"
        self.cpp_info.components["diagnostic_definitions"].names["cmake_find_package_multi"] = "diagnostic_definitions"
        self.cpp_info.components["diagnostic_definitions"].names["pkg_config"] = "boost_diagnostic_definitions"  # FIXME: disable on pkg_config
        # I would assume headers also need the define BOOST_LIB_DIAGNOSTIC, as a header can trigger an autolink,
        # and this definition triggers a print out of the library selected.  See notes below on autolink and headers.
        self.cpp_info.components["headers"].requires.append("diagnostic_definitions")

        self.cpp_info.components["disable_autolinking"].libs = []
        self.cpp_info.components["disable_autolinking"].set_property("cmake_target_name", "Boost::disable_autolinking")
        self.cpp_info.components["disable_autolinking"].names["cmake_find_package"] = "disable_autolinking"
        self.cpp_info.components["disable_autolinking"].names["cmake_find_package_multi"] = "disable_autolinking"
        self.cpp_info.components["disable_autolinking"].names["pkg_config"] = "boost_disable_autolinking"  # FIXME: disable on pkg_config

        # Even headers needs to know the flags for disabling autolinking ...
        # magic_autolink is an option in the recipe, so if a consumer wants this version of boost,
        # then they should not get autolinking.
        # Note that autolinking can sneak in just by some file #including a header with (eg) boost/atomic.hpp,
        # even if it doesn't use any part that requires linking with libboost_atomic in order to compile.
        # So a boost-header-only library that links to Boost::headers needs to see BOOST_ALL_NO_LIB
        # in order to avoid autolinking to libboost_atomic

        # This define is already imported into all of the _libboost libraries from this recipe anyway,
        # so it would be better to be consistent and ensure ANYTHING using boost (headers or libs) has consistent #defines.

        # Same applies for for BOOST_AUTO_LINK_{layout}:
        # consumer libs that use headers also need to know what is the layout/filename of the libraries.
        #
        # eg, if using the "tagged" naming scheme, and a header triggers an autolink,
        # then that header's autolink request had better be configured to request the "tagged" library name.
        # Otherwise, the linker will be looking for a (eg) "versioned" library name, and there will be a link error.

        # Note that "_libboost" requires "headers" so these defines will be applied to all the libraries too.
        self.cpp_info.components["headers"].requires.append("disable_autolinking")

        self.cpp_info.components["dynamic_linking"].libs = []
        self.cpp_info.components["dynamic_linking"].set_property("cmake_target_name", "Boost::dynamic_linking")
        self.cpp_info.components["dynamic_linking"].names["cmake_find_package"] = "dynamic_linking"
        self.cpp_info.components["dynamic_linking"].names["cmake_find_package_multi"] = "dynamic_linking"
        self.cpp_info.components["dynamic_linking"].names["pkg_config"] = "boost_dynamic_linking"  # FIXME: disable on pkg_config
        # A library that only links to Boost::headers can be linked into another library that links a Boost::library,
        # so for this reasons, the header-only library should know the BOOST_ALL_DYN_LINK definition as it will likely
        # change some important part of the boost code and cause linking errors downstream.
        # This is in the same theme as the notes above, re autolinking.
        self.cpp_info.components["headers"].requires.append("dynamic_linking")

        for module in self._dependencies["dependencies"]:
            self.cpp_info.components[module].set_property("cmake_target_name", "Boost::" + module)
            self.cpp_info.components[module].names["cmake_find_package"] = module
            self.cpp_info.components[module].names["cmake_find_package_multi"] = module
            self.cpp_info.components[module].names["pkg_config"] = f"boost_{module}"
