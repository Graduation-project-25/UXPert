import os

def export_to_csv(df, file_name, folder="./output"):
    # Ensure the output folder exists
    os.makedirs(folder, exist_ok=True)

    # Construct full path
    output_path = os.path.join(folder, file_name)

    # Save the Dataframe
    df.to_csv(output_path, index = False)

    print(f"Data saved to {output_path}")
