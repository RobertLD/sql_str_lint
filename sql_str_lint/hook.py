import argparse
from typing import Sequence
import libcst as cst
from utils.ast import StringTransformer
import importlib_resources
from sqlfluff.core.config import FluffConfig


def parse_file_to_ast(file_path: str):
    """Parse the content of a file into an Abstract Syntax Tree (AST) using the provided file path.

    ### Args:
        file_path (str): The path to the file to be parsed.

    ###Returns:
        MetadataWrapper: The AST of the file wrapped in a MetadataWrapper object.
    """
    with open(file_path, 'r') as file:
        file_ast = cst.parse_module(file.read())

        file_ast_w_metadata = cst.MetadataWrapper(file_ast)
    return file_ast_w_metadata


def lint_file_ast(file_ast,
                  fluff_config.
                  str_name_filter) -> cst.Module:
    """Lint the given file AST using a StringTransformer with the provided FluffConfig.

    ### Args:
        file_ast (cst.Module): The abstract syntax tree of the file to be linted.
        fluff_config (FluffConfig): The configuration settings for sqlfluff linting.

    ### Returns:
        cst.Module: The linted abstract syntax tree of the file.
    """
    linted_file_ast = file_ast.visit(StringTransformer(fluff_config,
                                                       str_name_filter,
                                                       file_ast.module.default_indent))
    return linted_file_ast


def write_linted_ast(file_ast: cst.Module, file_path: str) -> None:
    """Write the linted abstract syntax tree of the file to the specified file path.

    ### Args:
        file_ast (cst.Module): The linted abstract syntax tree of the file.
        file_path (str): The path to write the linted file.
    """
    with open(file_path, 'w') as f:
        linted_source = file_ast.code
        f.write(linted_source)


def main(argv: Sequence[str]):
    """Hook driver method."""
    args = process_arguments(argv)

    if not args.files:
        return
    if not args.config:
        fluff_config = FluffConfig.from_string(
            importlib_resources.read_text("sql_str_lint", ".sqlfluff")
        )
    else:
        fluff_config = FluffConfig.from_path(args.config)

    for file_path in args.files:
        file_ast = parse_file_to_ast(file_path)
        file_ast_fixed = lint_file_ast(file_ast,
                                       fluff_config,
                                       args.name_filter)
        write_linted_ast(file_ast_fixed, file_path)


def process_arguments(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", help="Filenames to lint/fix")
    parser.add_argument(
        "-c", "--config", help="Path to SQLFluff compatible config file"
    )
    parser.add_argument(
        "-n",
        "--name-filter",
        default='qry',
        help="Only string variables whose name contains this name will be linted"
    )
    args = parser.parse_args(argv)
    return args


if __name__ == '__main__':
    main()
