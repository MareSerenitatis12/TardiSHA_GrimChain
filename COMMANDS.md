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
  grimchain [NUMBER] --manifest FILE
  grimchain [NUMBER] --manifest DIRECTORY
  grimchain [NUMBER] -R --manifest DIRECTORY
  grimchain [NUMBER] --string --manifest "TEXT"
  grimchain [NUMBER] --pdf-embed PDF
  grimchain [NUMBER] --pdf-embed --manifest PDF
  grimchain --pdf-rm-embed PDF
  grimchain --help -a

NUMBER is chosen by you. It tells Grimchain how many Synodic Magicae characters to
place in the middle of the Grimchain. 64 is only an example. Leave NUMBER out
to use the Shadow Locus ⛎ middle.

basic use:
  grimchain PATH
      Grimchain one file or one directory.

  grimchain NUMBER PATH
      Grimchain one file or directory using the number of middle characters
      you choose.

  grimchain --string "TEXT"
  grimchain NUMBER --string "TEXT"
      Grimchain the exact UTF-8 content supplied by the quoted argument.
      The quotes belong to the shell and are not part of the source.
      No newline, trimming, or normalization is added.

  grimchain [NUMBER] --manifest FILE
      Create manifest-FILENAME.grim for the file, prepare its terminal THIS FILE
      line, append its exact same-width self-return, and print that Grimchain.

  grimchain [NUMBER] --manifest DIRECTORY
      Create manifest-DIRECTORYNAME.grim for the directory and its direct
      contents only, then append and print its exact same-width THIS FILE return.

  grimchain [NUMBER] -R --manifest DIRECTORY
      Create manifest-recurse-DIRECTORYNAME.grim for the complete recursive tree,
      then append and print its exact same-width THIS FILE return.

  grimchain [NUMBER] --string --manifest "TEXT"
      Create a self-returning .grim manifest from the exact UTF-8 string source.
      The manifest entry name is the exact shell argument supplied to --string.

  grimchain [NUMBER] --pdf-embed PDF
      Append the PDF GrimChain self-return to PDF. With NUMBER, the return uses
      that exact middle depth. Without NUMBER, it uses the Shadow Locus ⛎ middle.
      The PDF keeps its exact filename identity. The return is verified through
      the Aeternum Mirror before it is accepted.

  grimchain [NUMBER] --pdf-embed --manifest PDF
      Perform the normal PDF embed and print its Grimchain, then naturally return
      that PDF through the PDF Mirror path, create its self-returning .grim manifest,
      and print the manifest THIS FILE Grimchain.

  grimchain --pdf-rm-embed PDF
      Remove the existing verified terminal PDF GrimChain self-return from PDF.
      This is separate from --pdf-embed and accepts no NUMBER. It first verifies
      the existing terminal return, then restores the exact witnessed PDF body
      beneath that return. A missing or non-closing return is refused.
```

## Advanced help

```text
usage:
  grimchain [NUMBER] PATH [OPTIONS]
  grimchain [NUMBER] PATH [OPTIONS]
  grimchain --string "TEXT" [NUMBER]
  grimchain [NUMBER] --pdf-embed PDF

NUMBER is any non-negative whole number you choose. It controls how many
Synodic Magicae characters appear in the middle. 64 is an example, not a fixed size.
Leave NUMBER out to use the Shadow Locus ⛎ middle.

ordinary use:
  grimchain PATH
      Grimchain one file or directory with the Shadow Locus ⛎ middle.

  grimchain NUMBER PATH
  grimchain --middle NUMBER PATH
      Grimchain one file or directory with NUMBER middle characters.

  grimchain --string "TEXT"
  grimchain NUMBER --string "TEXT"
      Grimchain the exact UTF-8 content inside the quoted shell argument.
      The shell quotes are not part of the source. No newline, trimming,
      normalization, or separate string algorithm is added.

  grimchain NUMBER PATH --output FILE
      Save the Grimchain in FILE instead of printing it.

  grimchain PATH --verify --output FILE
      Check that FILE is the correct Grimchain for PATH.

manifests:
  grimchain [NUMBER] --manifest FILE
      Create manifest-FILENAME.grim with a terminal THIS FILE self-return.
      The selected middle is used for the manifest and its self-return.

  grimchain [NUMBER] --manifest DIRECTORY
      Create manifest-DIRECTORYNAME.grim for the directory and its direct
      contents only, append its exact same-width THIS FILE return, and print it.

  grimchain [NUMBER] -R --manifest DIRECTORY
      Create manifest-recurse-DIRECTORYNAME.grim for the complete recursive tree,
      append its exact same-width THIS FILE return, and print it.

  grimchain [NUMBER] --output FILE --manifest PATH
      Write the self-returning manifest to the filename you choose and print
      the exact Grimchain stored under its terminal THIS FILE line.

  grimchain [NUMBER] --verify --output FILE --manifest PATH
      Recreate the manifest information and check it against FILE.

  grimchain [NUMBER] --string --manifest "TEXT"
      Create a self-returning manifest from the exact UTF-8 string source.
      The manifest entry name is exactly the shell argument supplied to --string.

  grimchain [NUMBER] --string --output FILE --manifest "TEXT"
      Write that self-returning string manifest to FILE instead of its default
      manifest filename.

PDF self-return:
  grimchain [NUMBER] --pdf-embed PDF
      Append the exact PDF GrimChain self-return. The return is computed from the
      witnessed PDF body under its unchanged filename identity and is verified
      by complete Aeternum Mirror regeneration.

  grimchain [NUMBER] --pdf-embed --manifest PDF
      Perform the normal PDF embed first and print its normal Grimchain. Then the
      PDF completes its return through the PDF Mirror path, is Grimchained from
      that returned source, and receives a self-returning .grim manifest whose
      terminal THIS FILE Grimchain is printed after the PDF Grimchain.

  grimchain [NUMBER] --pdf-embed --output FILE --manifest PDF
      Perform the same PDF embed and write the resulting self-returning manifest
      to FILE.

  grimchain --pdf-rm-embed PDF
      Verify and remove only the terminal PDF GrimChain self-return, restoring
      the exact witnessed body. This command is independent of --pdf-embed and
      does not accept a middle NUMBER.

inspection and lists:
  grimchain SEAL --inspect
      Show the parts contained in one Grimchain.

input and optional controls:
  printf 'text' | grimchain [NUMBER]
      Grimchain text received through standard input.

  grimchain --binary PATH
      Read the file as exact bytes. This is the only file-body law; line endings
      and all other bytes are never normalized.

  grimchain PATH --nonce INTEGER
      Use the chosen integer to create another repeatable Grimchain for PATH.

  grimchain PATH --fold --span NUMBER --levels NUMBER
      Create the fold-ladder output for PATH. Both dimensions are explicit
      and required.

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
