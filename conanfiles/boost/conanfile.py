from conan import ConanFile
from conan.tools import files
from typing import Optional
from os import path


class BoostConan(ConanFile):
    name = "boost"
    version = "1.70.0"
    settings = "os", "compiler", "arch", "build_type"
    description = "Conan package for boost library"
    user = "pcl-android"
    channel = "stable"
    url = "https://www.boost.org/"
    license = "Boost Software License"
    folder_name = "boost_{}".format(version.replace(".", "_"))

    def _to_android_arch(self, arch: str) -> str:
        if arch == "armv7":
            return "armv7a"
        if arch == "armv8":
            return "aarch64"

        return arch

    def _to_android_address_model(self, arch: str) -> Optional[str]:
        if arch == "armv7":
            return "32"
        if arch == "armv8" or arch == "x86_64":
            return "64"

        return None

    def _to_boost_arch(self, arch: str) -> Optional[str]:
        if arch.startswith("arm") or arch == "aarch64":
            return "arm"
        if arch.startswith("x86"):
            return "x86"

        return None

    def _get_build_os(self, os: str):
        os = str(os).lower()

        if os == "macos":
            return "darwin"

        return os

    def _configure_user_config(self) -> None:
        if str(self.settings.arch) == "armv7":
            ext = "eabi"
        else:
            ext = ""

        build_os = self._get_build_os(self.settings_build.os)
        ndk_path = self.conf.get("tools.android:ndk_path")
        path_to_clang_compiler = "{}/toolchains/llvm/prebuilt/{}-x86_64/bin/{}-linux-android{}{}-clang++".format(
            ndk_path,
            build_os,
            self._to_android_arch(str(self.settings.arch)),
            ext, self.settings.os.api_level
        )

        print("Compiler: {}".format(path_to_clang_compiler))

        compiler_flags = "-fPIC -std=c++11 -stdlib=libc++"
        user_config = "using clang : androidos : {}\n: <cxxflags>\"{}\"\n;".format(path_to_clang_compiler, compiler_flags)
        path_to_user_config = "{}/{}/tools/build/src/user-config.jam".format(self.build_folder, self.folder_name)

        file = open(path_to_user_config, "w")
        file.write(user_config)
        file.close()

    def _configure_boost(self) -> None:
        self.run("./bootstrap.sh")

    def _build_boost(self) -> None:
        b2_comd = "./b2 link=static variant=release threading=multi --without-python --debug-configuration --abbreviate-paths architecture={} --stagedir={} target-os=android address-model={} abi=aapcs".format(
            self._to_boost_arch(str(self.settings.arch)),
            self.settings.arch,
            self._to_android_address_model(str(self.settings.arch))
        )

        self.run(b2_comd)

    def source(self):
        files.get(self, "https://boostorg.jfrog.io/artifactory/main/release/{}/source/{}.tar.gz".format(self.version, self.folder_name))

    def build(self):
        with files.chdir(self, self.folder_name):
            self._configure_user_config()
            self._configure_boost()
            self._build_boost()

    def package(self):
        files.copy(self, pattern="*.a", dst=path.join(self.package_folder, "lib"), src="{}/{}/lib".format(self.folder_name, self.settings.arch))
        files.copy(self, pattern="*", dst=path.join(self.package_folder , "include/boost"), src="{}/boost".format(self.folder_name))

    def package_info(self):
        self.cpp_info.libs = files.collect_libs(self)
