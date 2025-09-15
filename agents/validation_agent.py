from utils.data_validation import validate_data_structure

class ValidationAgent:
    def __init__(self):
        self.status = "Waiting for file upload"
    
    def process_data(self, df):
        """
        Process and validate the uploaded data
        """
        self.status = "Validating data structure..."
        validation_result, processed_df = validate_data_structure(df)
        self.status = "Validation complete"
        return validation_result, processed_df