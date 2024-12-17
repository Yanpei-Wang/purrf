load("@pypi//:requirements.bzl", "requirement")
load("@rules_python//python:defs.bzl", "py_binary", "py_library")

package(default_visibility = ["//flask_bazel_sample:__subpackages__"])

py_binary(
    name = "flask_bazel_sample",
    srcs = ["app.py"],
    main = "app.py",
    deps = [
        "@pypi//flask",
    ]
)

py_test(
    name = "app_test",
    srcs = ["app_test.py"],
    deps = [
        ":flask_bazel_sample",
    ],
)