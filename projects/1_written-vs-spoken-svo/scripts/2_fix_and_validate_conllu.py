from conllu import parse_incr

# Function to fix invalid IDs in a CoNLL-U file
def fix_invalid_ids(filepath, output_path):
    with open(filepath, "r", encoding="utf-8") as infile, open(output_path, "w", encoding="utf-8") as outfile:
        for line in infile:
            stripped_line = line.strip()
            if stripped_line.startswith("#"):  # Preserve metadata lines
                outfile.write(line + "\n")
            elif stripped_line == "":  # Preserve blank lines
                outfile.write("\n")
            else:
                fields = stripped_line.split("\t")
                if len(fields) == 10 and fields[0].isdigit():  # Validate token line
                    outfile.write("\t".join(fields) + "\n")
                else:
                    print(f"Skipping invalid line: {line.strip()}")  # Log invalid lines
    print(f"Fixed file saved to {output_path}")

# Function to validate a CoNLL-U file
def validate_conllu(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        try:
            for sentence in parse_incr(file):
                pass  # If this loops through, the file is valid
            print(f"File {filepath} is valid.")
        except Exception as e:
            print(f"File {filepath} is invalid: {e}")

# Paths for input, cleaned, and fixed files
cleaned_path = "data/src/sl_ssj-ud.conllu"
fixed_path = "data/src/fixed_sl_ssj-ud.conllu"

# Step 1: Fix invalid IDs
fix_invalid_ids(cleaned_path, fixed_path)

# Step 2: Validate the fixed file
validate_conllu(fixed_path)
