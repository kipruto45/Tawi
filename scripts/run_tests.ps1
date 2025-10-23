param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [String[]]
    $RemainingArgs
)

# Ensure Django settings are used and run tests via manage.py so Django's test runner
# sets up apps and test environment correctly.
$env:DJANGO_SETTINGS_MODULE = 'tawi_project.settings'

if ($null -eq $RemainingArgs -or $RemainingArgs.Count -eq 0) {
    Write-Host "Running: python manage.py test"
    & python manage.py test
} else {
    # Pass the argument array through so python receives each test label as a
    # separate argument (avoids joining them into one string which unittest
    # interprets as a single module name).
    Write-Host "Running: python manage.py test $($RemainingArgs -join ' ')"
    & python manage.py test @RemainingArgs
}
