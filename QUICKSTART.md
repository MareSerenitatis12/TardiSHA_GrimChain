# Quick Start

## Install the wheel

```bash
python -m pip install dist/tardisha-23.0.6-cp312-cp312-linux_x86_64.whl
```

## Seal a file

```bash
echo "The path out is the path back." > sample.txt
grimchain sample.txt
```

## Grimchain a quoted string

```bash
grimchain --string "The path out is the path back."
grimchain 64 --string "The path out is the path back."
```

The exact UTF-8 argument is used without an added newline.

## Demonstrate the natural fixed point

```bash
python examples/self_return_demo.py
```

The demonstration creates a temporary file, obtains its Grimchain, appends that exact result, and runs the same command again. Both results must match.

## Run the quick validator

```bash
python validation/validate_release.py
```

## Run the full validator

```bash
python validation/validate_release.py --full
```

## Work directly from source

```bash
python TardiSHA_selftest.py
./grimchain sample.txt
```

The local launchers use the package in this directory. Installing the wheel creates equivalent console commands in the active Python environment.
