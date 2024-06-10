## Python SQL Embedded String Linter

SQL String Linter is a tool designed to lint SQL strings within Python code using sqlfluff. It provides a way to parse Python files into Abstract Syntax Trees (AST), lint the SQL strings within the AST, and write back the linted code.

A working SQLFluff config is required for this hook and can be provided to the tool via path. Otherwise the embedded default will be used which may not be appropriate for your use case

The module is designed as a [pre-commit](https://github.com/pre-commit) hook.

Add this to your ``.pre-commit-config.yaml`` file

    - repo: git@github.com:RobertLD/sql_str_lint.git
      sha: 0.0.1
      hooks:
      - id: sql-str-lint

Available flags:

* ``--config``: File path for SQLfluff config file
* ``--name-filter`` Only lint str variables containing this sub-string

The hook supports [sqlfluff's configuration files](https://docs.sqlfluff.com/en/stable/configuration.html) - Please refer to the sqlfluff documentation for reference

## License:
This project is licensed under the MIT License. See the LICENSE file for more details.

## Acknowledgments:

The project uses sqlfluff for linting SQL strings.
