import difflib


def check_content_changes(old_content, new_content):
    """Checks for additions and deletions in the content."""
    # Split content into lines for comparison
    old_lines = old_content.splitlines()
    new_lines = new_content.splitlines()

    # Run unified_diff to get the differences
    diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=""))

    additions = []
    deletions = []

    # Parse the diff output
    for line in diff:
        print(line)
        if line.startswith('+') and not line.startswith('+++'):  # Exclude file header line with '+++'
            additions.append(line[1:])  # Exclude '+' symbol
        elif line.startswith('-') and not line.startswith('---'):  # Exclude file header line with '---'
            deletions.append(line[1:])  # Exclude '-' symbol

    return additions, deletions


# Example usage:
old_content = """Hello, world!
This is the old content.
Line to be removed."""

new_content = """Hello, world!
This is the new content.
Additional line here."""

# Check for changes
#additions, deletions = check_content_changes(old_content, new_content)

#print("Additions:", additions)
#print("Deletions:", deletions)

import hashlib
url = "https://careers.bcplatforms.com/jobs"
print(hashlib.md5(url.encode()).hexdigest()[:8] )

