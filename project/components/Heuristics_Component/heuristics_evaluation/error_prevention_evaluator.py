import pandas as pd
from components.Heuristics_Component.heuristics_evaluation.heuristic_evaluation import HeuristicEvaluationInterface
from components.Heuristics_Component.heuristic_rules.ErrorPrevention import ErrorPrevention

class ErrorPreventionEvaluation(HeuristicEvaluationInterface):    
    def evaluate_rule(self, designs):
        """Evaluate error prevention in the given designs."""
        self.evaluate_error_prevention(designs)

    def evaluate_error_prevention(self, designs):
        """Checks for missing validation messages and confirmation dialogs."""
        
        # Convert UI elements from JSON to DataFrame
        df = pd.DataFrame([elem for design in designs for elem in design['elements']])
        
        # Pass the dataframe to the error prevention checker
        error_checker = ErrorPrevention(df)
        error_report = error_checker.generate_error_prevention_report()
        
        print("\n Error Prevention Report:")
        print(error_report)

        # Identify missing validation issues
        validation_issues = error_checker.check_input_validation()
        print(f"\n Validation Issues: {validation_issues}")

        # Identify missing confirmation dialogs
        confirmation_issues = error_checker.check_confirmation_for_dangerous_actions()
        print(f"\n Confirmation Issues: {confirmation_issues}")
