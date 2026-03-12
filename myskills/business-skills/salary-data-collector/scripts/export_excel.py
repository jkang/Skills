import os
import sys
import json
import pandas as pd

def main():
    if len(sys.argv) < 2:
        print("Usage: python export_excel.py <company_name>")
        company_name = "Company"
    else:
        company_name = sys.argv[1]

    # Change to parent directory if script is run from within the tools directory
    # or resolve absolute paths relative to where it should be executed from.
    # The skill describes assuming files are in `reports/` relative to the CWD
    # We will compute the absolute path to reports/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    reports_dir = os.path.join(parent_dir, "reports")

    cleaned_data_path = os.path.join(reports_dir, "cleaned_data.json")
    raw_data_path = os.path.join(reports_dir, "raw_data_merged.json")
    output_excel_path = os.path.join(reports_dir, f"Salary_Report_{company_name}.xlsx")

    # Fallback to current directory reports if script path is weird
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir, exist_ok=True)

    def load_json(filepath):
        if not os.path.exists(filepath):
            print(f"Warning: File {filepath} not found.")
            return []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON {filepath}: {e}")
            return []

    cleaned_data = load_json(cleaned_data_path)
    raw_data = load_json(raw_data_path)

    df_cleaned = pd.DataFrame(cleaned_data)
    df_raw = pd.DataFrame(raw_data)

    try:
        # Create Excel writer
        with pd.ExcelWriter(output_excel_path, engine='openpyxl') as writer:
            if not df_cleaned.empty:
                df_cleaned.to_excel(writer, sheet_name='Cleaned Data', index=False)
            else:
                pd.DataFrame({"Message": ["No cleaned data found"]}).to_excel(writer, sheet_name='Cleaned Data', index=False)

            if not df_raw.empty:
                df_raw.to_excel(writer, sheet_name='Raw Data', index=False)
            else:
                pd.DataFrame({"Message": ["No raw data found"]}).to_excel(writer, sheet_name='Raw Data', index=False)

        print(f"Successfully generated Excel report at: {output_excel_path}")
    except Exception as e:
        print(f"Failed to generate Excel file: {e}")

if __name__ == "__main__":
    main()
