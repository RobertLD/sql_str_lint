import libcst as cst
from sqlfluff.core.config import FluffConfig
import sqlfluff
from libcst.metadata import WhitespaceInclusivePositionProvider, ParentNodeProvider


class StringTransformer(cst.CSTTransformer):
    """CSTTransformer class for transforming string assignments in Python code.

    ### Attributes:
        METADATA_DEPENDENCIES (tuple): A tuple containing the metadata dependencies required for the transformer.

    ### Args:
        fluff_config (FluffConfig): The configuration object for sqlfluff.
        magic_string (str): The magic string used to determine which strings to alter (default is 'qry').
        default_indent (str): The default indentation string (default is '    ').

    ### Methods:
        format_fixed_sql_string(linted_sql_str: str) -> str: Formats the fixed SQL string with appropriate quotes.
        visit_Assign(n: cst.Assign) -> bool: Visits and processes Assign nodes in the CST.
        leave_Assign(original_node: cst.Assign, updated_node: cst.Assign) -> cst.CSTNode: Processes and updates Assign nodes before leaving.
        calculate_indent(base_position: int, aditional_indent_levels: int) -> str: Calculates the indentation based on the base position and additional levels.
    """
    METADATA_DEPENDENCIES = (
        WhitespaceInclusivePositionProvider, ParentNodeProvider,)

    def __init__(self,
                 fluff_config: FluffConfig,
                 magic_string: str = 'qry',
                 default_indent: str = '    '):

        self.magic_sentinel_string = magic_string
        self.fluff_config = fluff_config
        self.fixed_sql_string = None
        self.quote_type = None
        self.default_indent = default_indent

    def format_fixed_sql_string(self, linted_sql_str: str):
        """Format the fixed SQL string with appropriate quotes.

        ### Args:
            linted_sql_str (str): The linted SQL string to be formatted.

        ### Returns:
            str: The formatted SQL string with appropriate quotes.
        """
        if len(self.quote_type) > 1:
            return f'{self.quote_type}\n{linted_sql_str}{self.quote_type}'
        else:
            return f'{self.quote_type}{linted_sql_str}{self.quote_type}'

    def visit_Assign(self, n: cst.Assign) -> bool:
        """Visit and process Assign nodes in the CST.

        ### Args:
            n (cst.Assign): The Assign node to be visited.

        ### Returns:
            bool: True if the node was successfully processed, False otherwise.
        """
        # Only consider where the rval is a string
        if not isinstance(n.value, cst.SimpleString):
            return False

        # user provided magic string for determining which strings to alter
        if not all([self.magic_sentinel_string in t.target.value for t in n.targets]):
            return False

        try:
            maybe_sql_string: str = n.value.evaluated_value
            self.quote_type: str = n.value.quote

            linted_sql_str = sqlfluff.fix(
                maybe_sql_string, config=self.fluff_config)

            self.fixed_sql_string = self.format_fixed_sql_string(
                linted_sql_str)

            return True
        except Exception:
            return False

    def leave_Assign(self, original_node: cst.Assign, updated_node: cst.Assign) -> cst.CSTNode:
        """Processe and update Assign nodes before leaving.

        ### Args:
            original_node (cst.Assign): The original Assign node.
            updated_node (cst.Assign): The updated Assign node.

        ### Returns:
            cst.CSTNode: The updated node with the new value.
        """
        if not self.fixed_sql_string:
            return original_node

        try:
            lval_indent = self.get_metadata(
                WhitespaceInclusivePositionProvider, original_node.targets[0]).start.column
        except Exception:
            lval_indent = 0

        rval_indent = self.calculate_indent(lval_indent, 1)

        formatted_fixed_sql_string = rval_indent.join(
            self.fixed_sql_string.splitlines(True))
        new_value_node = cst.SimpleString(formatted_fixed_sql_string)

        # Return the updated node with the new value
        return updated_node.with_changes(value=new_value_node)

    def calculate_indent(self, base_position: int, aditional_indent_levels: int) -> str:
        """Calculate the indentation based on the base position and additional levels.

        ### Args:
            base_position (int): The base position for calculating the current indent level.
            additional_indent_levels (int): The number of additional indent levels to be added.

        ### Returns:
            str: The calculated indentation string based on the base position and additional levels.
        """
        current_indent_level = base_position // len(self.default_indent)
        return (current_indent_level + aditional_indent_levels) * self.default_indent
