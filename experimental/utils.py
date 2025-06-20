import sys
import traceback


def print_error_with_line(error_message: str, error: Exception) -> None:
    """Print error message with line number information
    
    Args:
        error_message: Custom error message to display
        error: Exception to display with traceback information
    """
    # Get the current exception info
    exc_type, exc_value, exc_traceback = sys.exc_info()
    
    if exc_traceback is None:
        # If no current exception, just print the message
        print(f"{error_message}: {error}", file=sys.stderr)
        return
    
    # Get traceback details
    tb_list = traceback.extract_tb(exc_traceback)
    
    if tb_list:
        # Get the last frame (where the error occurred)
        last_frame = tb_list[-1]
        filename = last_frame.filename
        line_number = last_frame.lineno
        function_name = last_frame.name
        line_text = last_frame.line
        
        print(f"Error in {filename}:{line_number} in {function_name}()", file=sys.stderr)
        if line_text:
            print(line_text.rstrip(), file=sys.stderr)
        print(f"{error_message}: {exc_value}", file=sys.stderr)
    else:
        print(f"{error_message}: {error}", file=sys.stderr)
