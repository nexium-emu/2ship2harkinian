#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
    printf 'Usage: %s BASE_SHA HEAD_SHA\n' "$0" >&2
    exit 2
fi

base=$(git rev-parse --verify "$1^{commit}")
head=$(git rev-parse --verify "$2^{commit}")
merge_base=$(git merge-base "$base" "$head")
files=()

# Match run-clang-format.sh: ignore submodules, generated assets and decomp
# headers. Check only changed, tracked files so inherited formatting is separate.
while IFS= read -r -d '' path; do
    case "$path" in
        mm/assets/* | mm/src/*.h | mm/include/*.h) ;;
        mm/*.c | mm/*.cpp | mm/*.h) files+=("$path") ;;
    esac
done < <(git diff --name-only --diff-filter=ACMR -z "$merge_base" "$head" -- mm)

if [[ ${#files[@]} -eq 0 ]]; then
    printf 'No changed source files require formatting.\n'
    exit 0
fi

printf 'Checking %s source file(s) with clang-format-14.\n' "${#files[@]}"
clang-format-14 --dry-run --Werror -- "${files[@]}"
