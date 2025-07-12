# build_docs_local.ps1

param(
    [Parameter(Mandatory=$true)]
    [string]$DocsDir, # Path to 'docs' directory
    
    [Parameter(Mandatory=$false)]
    [string]$SourceCodeDir = ".\dcpmessage\" # Path to 'dcpmessage' source code (relative to repo root)
)

$curr_dir = Get-Location

Write-Host "Generating API documentation with sphinx-apidoc into '$DocsDir'..."
try {
    # -f: force overwrite existing files
    # -e: put each module in its own file
    # -M: no module table of contents
    sphinx-apidoc -o "$DocsDir" -f -e -M "$SourceCodeDir"
    Write-Host "sphinx-apidoc completed successfully."
} catch {
    Write-Error "Error running sphinx-apidoc: $_"
    exit 1
}

# --- Step 2: Build documentation ---
# Change to the docs directory to run make
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
    # Ensure to return to original directory even on error
    Set-Location $curr_dir
    exit 1
}

# --- Return to original directory ---
Write-Host "Returning to original directory: $curr_dir"
Set-Location $curr_dir

Write-Host "Local documentation build script finished."