import os

def combine_files(root_dir, output_file):
    # Get absolute path of the output file before creating it
    abs_output = os.path.abspath(output_file)
    
    with open(abs_output, 'w', encoding='utf-8') as outfile:
        for root, _, files in os.walk(root_dir):
            for f in files:
                filepath = os.path.abspath(os.path.join(root, f))
                
                # Skip the output file so it doesn't read itself
                if filepath == abs_output:
                    continue
                
                # Get the relative path for a cleaner file tree look
                rel_path = os.path.relpath(filepath, root_dir)
                
                # Write a clean separator with the filename
                outfile.write(f"\n\n{'='*60}\n")
                outfile.write(f"File: {rel_path}\n")
                outfile.write(f"{'='*60}\n\n")
                
                # Let any error crash the script so you see exactly why it is failing
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
                    outfile.write(infile.read())

combine_files('.', 'TardiSHA_GrimChain_FINAL_SETAT+4D.txt')