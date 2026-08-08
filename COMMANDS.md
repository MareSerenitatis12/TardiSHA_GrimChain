# Grimchain Commands

The same command lists are available in the terminal:

```bash
grimchain --help
grimchain --help -a
```

## Basic help

```text
usage:
  grimchain PATH
  grimchain NUMBER PATH
  grimchain --string "TEXT"
  grimchain NUMBER --string "TEXT"
  grimchain NUMBER PATH --manifest
  grimchain NUMBER -R DIRECTORY --manifest
  grimchain --help -a

NUMBER is chosen by you. It tells Grimchain how many Synodic Magicae characters to
place in the middle of the Grimchain. 64 is only an example. Leave NUMBER out
to use the compact ⟠ middle.

basic use:
  grimchain PATH
      Grimchain one file or one directory.

  grimchain NUMBER PATH
      Grimchain one file or directory using the number of middle characters
      you choose.

  grimchain --string "TEXT"
  grimchain NUMBER --string "TEXT"
      Grimchain the exact UTF-8 content supplied by the quoted argument.
      No newline or normalization is added.

  grimchain NUMBER FILE --manifest
      Create manifest-FILENAME.grim, prepare its terminal THIS FILE line,
      append its exact same-width self-return, and print that same Grimchain.

  grimchain NUMBER DIRECTORY --manifest
      Create manifest-DIRECTORYNAME.grim for the files directly inside that
      directory, then append and print its exact same-width THIS FILE return.

  grimchain NUMBER -R DIRECTORY --manifest
      Create manifest-recurse-DIRECTORYNAME.grim for all subdirectories, then
      append and print its exact same-width THIS FILE return.
```

## Advanced help

```text
usage:
  grimchain [NUMBER] PATH [OPTIONS]
  grimchain [NUMBER] --string "TEXT" [OPTIONS]

NUMBER is any non-negative whole number you choose. It controls how many
Synodic Magicae characters appear in the middle. 64 is an example, not a fixed size.
Leave NUMBER out to use the compact ⟠ middle.

ordinary use:
  grimchain PATH
      Grimchain one file or directory with the compact ⟠ middle.

  grimchain NUMBER PATH
  grimchain --middle NUMBER PATH
      Grimchain one file or directory with NUMBER middle characters.

  grimchain --string "TEXT"
  grimchain NUMBER --string "TEXT"
      Grimchain the exact UTF-8 content inside the quoted shell argument.
      The shell quotes are not part of the source, and no newline is added.

  grimchain NUMBER PATH --output FILE
      Save the Grimchain in FILE instead of printing it.

  grimchain PATH --verify --output FILE
      Check that FILE is the correct Grimchain for PATH.

manifests:
  grimchain [NUMBER] FILE --manifest
      Create manifest-FILENAME.grim with a terminal THIS FILE self-return.
      The same selected middle is used and the same Grimchain is printed.

  grimchain [NUMBER] DIRECTORY --manifest
      Create manifest-DIRECTORYNAME.grim for direct files, append its exact
      same-width THIS FILE return, and print that return.

  grimchain [NUMBER] -R DIRECTORY --manifest
      Create manifest-recurse-DIRECTORYNAME.grim for the complete tree, append
      its exact same-width THIS FILE return, and print that return.

  grimchain [NUMBER] PATH --manifest --output FILE
      Write the self-returning manifest to the filename you choose and print
      the exact Grimchain stored under its terminal THIS FILE line.

  grimchain [NUMBER] PATH --manifest --verify --output FILE
      Recreate the manifest information and check it against FILE.

inspection and lists:
  grimchain SEAL --inspect
      Show the parts contained in one Grimchain.

  grimchain -c LIST
  grimchain --check LIST
      Check a list whose lines contain: GRIMCHAIN  PATH

input and optional controls:
  printf 'text' | grimchain [NUMBER]
      Grimchain text received through standard input.

  grimchain --binary PATH
      Use the file's exact bytes. This is the default.

  grimchain --text PATH
      Treat CRLF, CR, and LF line endings as the same before Grimchaining.

  grimchain PATH --nonce INTEGER
      Use the chosen integer to create another repeatable Grimchain for PATH.

  grimchain PATH --fold --span NUMBER --levels NUMBER
      Create the fold-ladder output for PATH.

  grimchain PATH1 PATH2 DIRECTORY
      Grimchain several sources in one command.

information:
  grimchain --version
      Show the installed TardiSHA version.

  grimchain --help
      Show basic use.

  grimchain --help -a
      Show all commands.
```
