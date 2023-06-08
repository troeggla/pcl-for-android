from conan import ConanFile, tools
from os import path


class PclConan(ConanFile):
    name = "pcl"
    version = "1.13.0"
    settings = "os", "compiler", "arch", "build_type"
    description = "Conan Package for pcl"
    user = "pcl-android"
    channel = "stable"
    license = "BSD"
    url = "http://www.pointclouds.org/"
    exports_sources = ["no-build-binaries.patch"]

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
        print("COMPONENTS:")
        print(self.dependencies["boost"].cpp_info.components["filesystem"].serialize())

        cmake.configure({
            "Boost_NO_SYSTEM_PATHS": "TRUE",
            "Boost_NO_BOOST_CMAKE": "TRUE",
            "Boost_USE_STATIC_LIBS": "TRUE",
            "PCL_SHARED_LIBS": "OFF",
            "PCL_BINARIES": "OFF",
            "WITH_CUDA": "OFF",
            "WITH_OPENGL": "OFF",
            "WITH_PCAP": "OFF",
            "WITH_PNG": "OFF",
            "WITH_QHULL": "OFF",
            "WITH_VTK": "OFF",
            "FLANN_USE_STATIC": "ON",
        })

        return cmake

    def generate(self):
        deps = tools.cmake.CMakeDeps(self)
        deps.set_property("boost", "cmake_target_name", "Boost::boost")
        deps.set_property("boost::filesystem", "cmake_target_name", "Boost::filesystem")
        deps.set_property("flann", "cmake_target_name", "FLANN::FLANN")
        deps.generate()

        toolchain = tools.cmake.CMakeToolchain(self)

        toolchain.variables["ANDROID_STL"] = "c++_static"
        toolchain.variables["ANDROID_TOOLCHAIN"] = self.settings.compiler
        toolchain.variables["ANDROID_PLATFORM"] = self._to_android_platform(self.settings.os.api_level)
        toolchain.variables["ANDROID_ABI"] = self._to_android_abi(str(self.settings.arch))

        toolchain.generate()

    def layout(self):
        tools.cmake.cmake_layout(self)

    def requirements(self):
        self.requires("boost/1.76.0@pcl-android/stable")
        self.requires("flann/1.9.2@pcl-android/stable")
        self.requires("eigen/3.3.7")

    def source(self):
        git = tools.scm.Git(self)
        git.fetch_commit(
            "https://github.com/PointCloudLibrary/pcl.git",
            f"{self.name}-{self.version}"
        )

        tools.files.patch(self, patch_file="no-build-binaries.patch")

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        tools.files.copy(
            self,
            pattern="*.a",
            dst=path.join(self.package_folder, "lib"),
            src=path.join(self.build_folder, "lib")
        )

        tools.files.copy(
            self,
            pattern="*",
            dst=path.join(self.package_folder, "include"),
            src=path.join(self.build_folder, "include")
        )

    def package_info(self):
        self.cpp_info.libs = tools.files.collect_libs(self)
