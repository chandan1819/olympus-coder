"""Debug context validation."""

from context_validator import ContextValidator, ProjectContext

file_paths = [
    "config/settings.json",
    "data/input.csv"
]

context = ProjectContext(file_paths)
validator = ContextValidator(context)

invalid_python_code = '''
def load_config():
    with open("config/nonexistent.json", "r") as f:
        return json.load(f)
'''

result = validator.validate_file_references(invalid_python_code, "python")
print("File reference validation result:")
for key, value in result.items():
    print(f"  {key}: {value}")

print("\nAvailable files:")
for file_path in context.file_paths:
    print(f"  {file_path}")

print("\nSimilar files for 'config/nonexistent.json':")
similar = validator._find_similar_files("config/nonexistent.json")
print(f"  {similar}")

print("\nTesting similarity calculation:")
target = "nonexistent.json"
candidate = "settings.json"
similarity = validator._calculate_similarity(target, candidate)
print(f"  Similarity between '{target}' and '{candidate}': {similarity}")

print("\nTesting file name matching:")
target_name = "nonexistent.json"
for file_path in context.file_paths:
    file_name = file_path.split('/')[-1]
    print(f"  Checking '{target_name}' vs '{file_name}'")
    if target_name in file_name or file_name in target_name:
        print(f"    -> Substring match found")
    similarity = validator._calculate_similarity(target_name, file_name)
    print(f"    -> Similarity: {similarity}")