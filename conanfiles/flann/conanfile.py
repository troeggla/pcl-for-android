from conan import ConanFile, tools
from os import path


class FlannConan(ConanFile):
    name = "flann"
    version = "1.9.1"
    settings = "os", "compiler", "arch", "build_type"
    description = "Conan package for flann library"
    url = "http://www.cs.ubc.ca/research/flann/"
    license = "BSD"

    def _to_android_abi(self, arch: str) -> str:
        if arch == "armv7":
            return "armeabi-v7a"
        if arch == "armv8":
            return "arm64-v8a"

        return arch

    def _to_android_platform(self, api_level: str) -> str:
        return "android-{}".format(api_level)

    def _configure_cmake(self):
        cmake = tools.cmake.CMake(self)

        cmake.configure({
            "BUILD_C_BINDINGS": "OFF",
            "BUILD_PYTHON_BINDINGS": "OFF",
            "BUILD_MATLAB_BINDINGS": "OFF",
            "BUILD_EXAMPLES": "OFF",
            "BUILD_TESTS": "OFF",
            "BUILD_DOC": "OFF"
        })

        return cmake

    def generate(self):
        toolchain = tools.cmake.CMakeToolchain(self)

        toolchain.variables["ANDROID_STL"] = "c++_shared"
        toolchain.variables["ANDROID_TOOLCHAIN"] = self.settings.compiler
        toolchain.variables["ANDROID_PLATFORM"] = self._to_android_platform(self.settings.os.api_level)
        toolchain.variables["ANDROID_ABI"] = self._to_android_abi(str(self.settings.arch))

        toolchain.generate()

    def requirements(self):
        self.requires("lz4/1.9.1")

    def source(self):
        git = tools.scm.Git(self)
        git.fetch_commit("https://github.com/mariusmuja/flann.git", self.version)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        tools.files.copy(self, pattern="*.a", dst=path.join(self.package_folder, "lib"), src="lib")
        tools.files.copy(self, pattern="*", dst=path.join(self.package_folder, "include"), src=path.join(self.build_folder, "include"))

        # add lz4 as transtive dependency
        tools.files.copy(self, pattern="*.a", src=self.dependencies["lz4"].cpp_info.libdirs[0], dst=path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = tools.files.collect_libs(self)
