#!/usr/bin/env python3

import sys
import re
import json
import argparse

from example_operations import examples_save_to_file


def process_example(file_path, examples):
    """Process example from a file and add to examples

    Arguments:
        file_path {Filepath} -- Filepath to Makefile describing example
        examples {Examples} -- List of examples where new example should be 
                               appended
    """
    with open(file_path, 'r') as file:
        content = "".join(file.readlines())

        # File data
        file_local_path = re.sub(r"\S+\/[0-9]+\.[0-9]\.[0-9]\/", "", file_path)
        file_sdk_version = re.findall(
            r"\/([0-9]+\.[0-9]\.[0-9])\/", file_path)[0]
        file_sources = set()
        file_includes = set()
        file_cflags = set()
        file_asmflags = set()
        file_ldflags = set()

        # Remove comments
        content = re.sub(r"#.*\n", "", content)

        # Find all sources (first regexp find SRC_FILES += .. \ .. \.. block, second extracts path)
        for sources in re.findall(r"SRC_FILES[ \t]*\+=(?:(?:[ \t]*\\[ \t]*\n)|(?:[ \t]*\S+[ \t]*(?:\\[ \t]*\n)?))+", content):
            sources = re.findall(r"\$\(SDK_ROOT\)\/(\S+)", sources)
            file_sources.update(sources)

        # Find all includes (first regexp find SRC_FILES += .. \ .. \.. block, second extracts path)
        for includes in re.findall(r"INC_FOLDERS[ \t]*\+=(?:(?:[ \t]*\\[ \t]*\n)|(?:[ \t]*\S+[ \t]*(?:\\[ \t]*\n)?))+", content):
            includes = re.findall(r"\$\(SDK_ROOT\)\/(\S+)", includes)
            file_includes.update(includes)

        # Find all c flags
        for cflags in re.findall(r"CFLAGS[ \t]*\+=(?:(?:[ \t]*\\[ \t]*\n)|(?:[ \t]*\S+[ \t]*(?:\\[ \t]*\n)?))+", content):
            cflags = re.findall(r"-\S+", cflags)
            for cflag in cflags:
                file_cflags.update(cflag.split(","))

        # Find all asm flags
        for asmflags in re.findall(r"ASMFLAGS[ \t]*\+=(?:(?:[ \t]*\\[ \t]*\n)|(?:[ \t]*\S+[ \t]*(?:\\[ \t]*\n)?))+", content):
            asmflags = re.findall(r"-\S+", asmflags)
            for cflag in asmflags:
                file_asmflags.update(cflag.split(","))

        # Find all ld flags
        for ldflags in re.findall(r"LDFLAGS[ \t]*\+=(?:(?:[ \t]*\\[ \t]*\n)|(?:[ \t]*\S+[ \t]*(?:\\[ \t]*\n)?))+", content):
            ldflags = re.findall(r"-\S+", ldflags)
            for cflag in ldflags:
                file_ldflags.update(cflag.split(","))

        # Convert to list and sort
        file_sources = list(file_sources)
        file_sources.sort()
        file_includes = list(file_includes)
        file_includes.sort()
        file_cflags = list(file_cflags)
        file_cflags.sort()
        file_asmflags = list(file_asmflags)
        file_asmflags.sort()
        file_ldflags = list(file_ldflags)
        file_ldflags.sort()

        examples.append({
            "path": file_path,
            "local_path": file_local_path,
            "sdk_version": file_sdk_version,
            "sources": file_sources,
            "includes": file_includes,
            "cflags": file_cflags,
            "asmflags": file_asmflags,
            "ldflags": file_ldflags
        })


# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("--output")
args = parser.parse_args()

# Scrape examples
examples = []
for line in sys.stdin.readlines():
    paths = line.split(" ")
    for path in paths:
        file_path = path.strip()
        if file_path != '':
            process_example(file_path, examples)

# Save them to a file
examples_save_to_file(args.output, examples)
