import os
import json
from pathlib import Path
from datetime import datetime

def get_file_extension(filename):
    """Extract the file extension from a filename."""
    return Path(filename).suffix

def generate_new_name(prefix, index, extension, padding=3):
    """
    Generate a new filename with prefix, number, and extension.
    
    Args:
        prefix: String prefix for the filename
        index: Numeric index for sequencing
        extension: File extension (including the dot)
        padding: Number of digits for zero-padding (default: 3)
    
    Returns:
        New filename as a string
    """
    return f"{prefix}_{str(index).zfill(padding)}{extension}"

def check_name_conflicts(directory, new_names, original_files):
    """
    Check if any new names would conflict with existing files.
    
    Args:
        directory: Path to the target directory
        new_names: List of proposed new filenames
        original_files: List of original filenames
    
    Returns:
        List of conflicting filenames (empty if no conflicts)
    """
    conflicts = []
    existing_files = set(os.listdir(directory))
    
    for new_name in new_names:
        # Check if new name exists and is not one of the files being renamed
        if new_name in existing_files and new_name not in original_files:
            conflicts.append(new_name)
    
    return conflicts

def bulk_rename_files(directory, prefix, file_extension=None, start_index=1, dry_run=True):
    """
    Rename all files in a directory with a custom prefix and sequential numbering.
    
    Args:
        directory: Path to the directory containing files to rename
        prefix: Prefix to add to each filename
        file_extension: Optional filter to rename only files with specific extension (e.g., '.jpg')
        start_index: Starting number for the sequence (default: 1)
        dry_run: If True, only preview changes without renaming (default: True)
    
    Returns:
        Dictionary with success status and list of changes made
    """
    try:
        # Validate directory exists
        if not os.path.isdir(directory):
            return {
                "success": False,
                "error": f"Directory not found: {directory}",
                "changes": []
            }
        
        # Get all files in directory (excluding subdirectories)
        all_items = os.listdir(directory)
        files = [f for f in all_items if os.path.isfile(os.path.join(directory, f))]
        
        # Filter by extension if specified
        if file_extension:
            if not file_extension.startswith('.'):
                file_extension = '.' + file_extension
            files = [f for f in files if f.lower().endswith(file_extension.lower())]
        
        # Sort files for consistent ordering
        files.sort()
        
        if not files:
            return {
                "success": False,
                "error": "No files found to rename",
                "changes": []
            }
        
        # Generate new filenames
        rename_plan = []
        new_names = []
        
        for idx, old_name in enumerate(files, start=start_index):
            extension = get_file_extension(old_name)
            new_name = generate_new_name(prefix, idx, extension)
            new_names.append(new_name)
            
            old_path = os.path.join(directory, old_name)
            new_path = os.path.join(directory, new_name)
            
            rename_plan.append({
                "old_name": old_name,
                "new_name": new_name,
                "old_path": old_path,
                "new_path": new_path
            })
        
        # Check for naming conflicts
        conflicts = check_name_conflicts(directory, new_names, files)
        if conflicts:
            return {
                "success": False,
                "error": f"Name conflicts detected: {', '.join(conflicts)}",
                "changes": rename_plan
            }
        
        # Preview mode - don't actually rename
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "message": "Preview mode - no files renamed",
                "changes": rename_plan
            }
        
        # Perform actual renaming
        successful_renames = []
        failed_renames = []
        
        for item in rename_plan:
            try:
                os.rename(item["old_path"], item["new_path"])
                successful_renames.append(item)
            except Exception as e:
                failed_renames.append({
                    **item,
                    "error": str(e)
                })
        
        return {
            "success": len(failed_renames) == 0,
            "dry_run": False,
            "successful": len(successful_renames),
            "failed": len(failed_renames),
            "changes": successful_renames,
            "errors": failed_renames
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "changes": []
        }

# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("BULK FILE RENAMER")
    print("=" * 60)
    print()
    
    # Ask user for input
    target_directory = input("Enter folder path (or press Enter for current folder): ").strip()
    if not target_directory:
        target_directory = "C:/Users/spoor/OneDrive/Desktop/my_test_files"  # Default folder
    
    file_prefix = input("Enter prefix for files (e.g., photo, document): ").strip()
    if not file_prefix:
        file_prefix = "file"  # Default prefix
    
    ext_input = input("Filter by extension? (e.g., .jpg or press Enter for all files): ").strip()
    extension_filter = ext_input if ext_input else None
    
    print("=" * 60)
    
    # First, run in preview mode (dry_run=True)
    print("\n[PREVIEW MODE - No files will be renamed]\n")
    result = bulk_rename_files(
        directory=target_directory,
        prefix=file_prefix,
        file_extension=extension_filter,
        start_index=1,
        dry_run=True
    )
    
    if result["success"]:
        print(f"Found {len(result['changes'])} files to rename:\n")
        for change in result["changes"]:
            print(f"  {change['old_name']} → {change['new_name']}")
        
        # Actually perform the rename
        print("\n[EXECUTING RENAME...]\n")
        result = bulk_rename_files(
            directory=target_directory,
            prefix=file_prefix,
            file_extension=extension_filter,
            start_index=1,
            dry_run=False
        )
        
        if result["success"]:
            print(f"✓ Successfully renamed {result['successful']} files!")
        else:
            print(f"✗ {result['failed']} files failed to rename")
            for error in result.get("errors", []):
                print(f"  Error: {error['old_name']} - {error['error']}")
    else:
        print(f"✗ Error: {result['error']}")
    
    print("\n" + "=" * 60)