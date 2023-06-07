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
    exports_sources = ["no-pkg-config.patch"]

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

        boost_include_dir = self.dependencies["boost"].cpp_info.includedirs[0]
        boost_lib_dir = self.dependencies["boost"].cpp_info.libdirs[0]
        # flann_include_dir = self.dependencies["flann"].cpp_info.includedirs[0]
        # flann_lib_dir = self.dependencies["flann"].cpp_info.libdirs[0]
        eigen_include_dir = path.join(
            self.dependencies["eigen"].cpp_info.includedirs[0],
            "eigen3"
        )

        cmake.configure({
            "Boost_NO_SYSTEM_PATHS": "ON",
            "PCL_SHARED_LIBS": "OFF",
            "PCL_BINARIES": "OFF",
            "WITH_CUDA": "OFF",
            "WITH_OPENGL": "OFF",
            "WITH_PCAP": "OFF",
            "WITH_PNG": "OFF",
            "WITH_QHULL": "OFF",
            "WITH_VTK": "OFF",
            "Boost_NO_SYSTEM_PATHS": "TRUE",
            "Boost_NO_BOOST_CMAKE": "TRUE",
            "Boost_USE_STATIC_LIBS": "TRUE",
            "EIGEN_INCLUDE_DIR": eigen_include_dir,
            "FLANN_USE_STATIC": "ON",
            # "FLANN_INCLUDE_DIR": flann_include_dir,
            # "FLANN_LIBRARY": f"{flann_lib_dir}/libflann_cpp_s.a;{flann_lib_dir}/liblz4.a"
        })

        return cmake

    def generate(self):
        deps = tools.cmake.CMakeDeps(self)
        deps.set_property("boost", "cmake_target_name", "Boost::boost")
        deps.set_property("boost::filesystem", "cmake_target_name", "Boost::filesystem")
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
        self.requires("boost/1.70.0@pcl-android/stable")
        # self.requires("flann/1.9.1@pcl-android/stable")
        self.requires("eigen/3.3.7")

    def source(self):
        git = tools.scm.Git(self)
        git.fetch_commit(
            "https://github.com/PointCloudLibrary/pcl.git",
            f"{self.name}-{self.version}"
        )

        tools.files.patch(self, patch_file="no-pkg-config.patch")

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
