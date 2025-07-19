# build_doc.ps1

param(
    [Parameter(Mandatory=$true)]
    [Alias("d")]
    [string]$DocsDir, # Path to 'docs' directory

    [Parameter(Mandatory=$false)]
    [Alias("s")]
    [string]$SourceCodeDir = ".\dcpmessage\" # Unused now but kept for future
)

$curr_dir = Get-Location

# --- Step 1: Skip sphinx-apidoc ---
Write-Host "Skipping sphinx-apidoc (you are manually documenting one class only)."

# --- Step 2: Build documentation ---
Write-Host "Changing directory to: $DocsDir"
Set-Location $DocsDir

Write-Host "Building documentation..."
try {
    Write-Host "Running 'make clean'..."
    .\make clean

    Write-Host "Running 'make html'..."
    .\make html

    Write-Host "Documentation build completed successfully."
} catch {
    Write-Error "Error building documentation: $_"
    Set-Location $curr_dir
    exit 1
}

# --- Return to original directory ---
Write-Host "Returning to original directory: $curr_dir"
Set-Location $curr_dir

Write-Host "Local documentation build script finished."
