input_file = "data/src/fixed_sl_ssj-ud.conllu"
output_file = "data/src/cleaned_sl_ssj-ud.conllu"

# Function to remove punctuation and PUNCT relation, and save the result
def remove_punctuation_and_punct_relation(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            # Skip punctuation lines with PUNCT relation
            if line.strip() and not line.startswith('#') and '\tPUNCT\t' in line:
                continue  # Skip punctuation lines
            outfile.write(line)  # Write the non-punctuation line to the output file

# Call the function to process the file and save the output
remove_punctuation_and_punct_relation(input_file, output_file)

# Notify the user that the file has been processed
print(f"Processed file saved at {output_file}")