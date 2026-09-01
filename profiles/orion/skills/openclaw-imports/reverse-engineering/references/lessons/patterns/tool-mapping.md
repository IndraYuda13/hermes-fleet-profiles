# Tool Mapping Discipline for Reverse Engineering Work

## Why this exists

Long-running RE tasks often waste time after resets because the available helper stack has to be rediscovered. A lightweight tool map prevents that.

## Minimum mapping fields

For each relevant tool/helper, capture:
- name
- status: installed / partial / missing
- main use
- when to use it
- caveats / blockers

## Recommended buckets

### Static Java / APK reading
- jadx
- apktool
- baksmali / smali

### Native static analysis
- Ghidra analyzeHeadless
- PyGhidra
- optional MCP helpers

### Dynamic / semi-dynamic analysis
- Unidbg harnesses
- Frida / frida-tools
- adb / Android runtime target

### Packaging / patching
- apktool rebuild
- apksigner
- zipalign if needed

## Operational rule

Whenever a new tool is installed or verified, update the map immediately with current reality.

## Distilled lesson

A current tool map is part of the investigation state, not optional documentation.
