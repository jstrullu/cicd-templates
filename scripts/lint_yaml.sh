#!/usr/bin/env bash
# Lint all Azure Pipelines YAML files using yamllint.
# Preprocesses files to replace Azure Pipelines template expressions
# (${{ ... }} and $[ ... ]) with placeholders before linting.
set -euo pipefail

OPEN_BRACE='${{'
DOLLAR_BRACKET='$['

exit_code=0
for file in $(find azure-pipelines -name '*.yml'); do
  # Replace Azure Pipelines expressions with placeholders so yamllint
  # can parse the file without false-positive errors.
  sed \
    -e "s/${OPEN_BRACE}[^}]*}}/PLACEHOLDER/g" \
    -e "s/\\${DOLLAR_BRACKET}[^]]*\\]/PLACEHOLDER/g" \
    "$file" > /tmp/lint_target.yml

  if ! yamllint -c .yamllint.yml /tmp/lint_target.yml; then
    echo "::error file=$file::yamllint failed"
    exit_code=1
  fi
done
exit $exit_code
