from setuptools import Extension, setup

setup(
    ext_modules=[
        Extension(
            "TardiSHA._alqc_kernel",
            sources=["TardiSHA/_alqc_kernel.c"],
            optional=True,
        )
    ]
)
