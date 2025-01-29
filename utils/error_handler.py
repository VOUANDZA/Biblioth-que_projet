from tkinter import messagebox
import traceback

class LibraryError(Exception):
    def __init__(self, code, message, details=None):
        self.code = code
        self.message = message
        self.details = details
        super().__init__(self.message)

class ErrorHandler:
    def __init__(self, logger):
        self.logger = logger
    
    def handle_error(self, error, user_id=None):
        if isinstance(error, LibraryError):
            self.logger.log_error(
                f"ERROR_{error.code}",
                user_id,
                {'message': error.message, 'details': error.details}
            )
            messagebox.showerror(
                f"Erreur {error.code}",
                error.message
            )
        else:
            error_details = {
                'type': type(error).__name__,
                'message': str(error),
                'traceback': traceback.format_exc()
            }
            self.logger.log_error(
                'UNEXPECTED_ERROR',
                user_id,
                error_details
            )
            messagebox.showerror(
                "Erreur inattendue",
                "Une erreur inattendue s'est produite. Veuillez réessayer."
            ) 