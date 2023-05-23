from conan import ConanFile, tools
from os import path


class Lz4Conan(ConanFile):
    name = "lz4"
    version = "1.9.1"
    user = "pcl-android"
    channel = "stable"
    settings = "os", "compiler", "arch", "build_type"
    description = "Conan package for lz4 library"
    url = "https://github.com/lz4/lz4/"
    license = "BSD 2-Clause"
    exports_sources = ["CMakeLists.txt"]

    def _to_android_abi(self, arch: str) -> str:
        if arch == "armv7":
            return "armeabi-v7a"
        if arch == "armv8":
            return "arm64-v8a"

        return arch

    def _to_android_platform(self, api_level: str) -> str:
        return "android-{}".format(api_level)

    def generate(self):
        toolchain = tools.cmake.CMakeToolchain(self)

        toolchain.variables["ANDROID_STL"] = "c++_shared"
        toolchain.variables["ANDROID_TOOLCHAIN"] = self.settings.compiler
        toolchain.variables["ANDROID_PLATFORM"] = self._to_android_platform(self.settings.os.api_level)
        toolchain.variables["ANDROID_ABI"] = self._to_android_abi(str(self.settings.arch))

        toolchain.generate()

    def source(self):
        git = tools.scm.Git(self)
        git.fetch_commit("https://github.com/lz4/lz4.git", "v1.9.1")

    def build(self):
        cmake = tools.cmake.CMake(self)

        cmake.configure()
        cmake.build()

    def package(self):
        tools.files.copy(self, pattern="*.a", dst=path.join(self.package_folder, "lib"), src=self.source_folder)
        tools.files.copy(self, pattern="lz4.h", dst=path.join(self.package_folder, "include"), src=path.join(self.source_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = tools.files.collect_libs(self)
