param([switch]$Probe)

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$project = (Resolve-Path (Join-Path $here '..\..')).Path
$python = Join-Path $project '.venv\Scripts\python.exe'
$runner = Join-Path $here 'run_full_balanced_lr.py'
$statusPath = Join-Path $here 'full_100gen_80pop_balancedLR_status.json'
$watchLog = Join-Path $here 'balancedLR_parallel_switch.log'

function Write-WatchLog([string]$message) {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $message"
    Add-Content -LiteralPath $watchLog -Value $line -Encoding UTF8
    Write-Output $line
}

function Get-RunStatus {
    if (-not (Test-Path -LiteralPath $statusPath)) { return $null }
    try {
        return Get-Content -LiteralPath $statusPath -Raw | ConvertFrom-Json
    } catch {
        # The runner rewrites this small JSON file every 30 seconds.
        return $null
    }
}

function Get-RunProcesses {
    return @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" | Where-Object {
        $_.CommandLine -and $_.CommandLine.Contains($here) -and (
            $_.CommandLine.Contains('run_full_balanced_lr.py') -or
            ($_.CommandLine.Contains('main.py') -and
             $_.CommandLine.Contains('--content-balance listening_reading'))
        )
    })
}

function Get-MemoryHeadroom {
    $os = Get-CimInstance Win32_OperatingSystem
    $samples = (Get-Counter '\Memory\Committed Bytes', '\Memory\Commit Limit' -SampleInterval 1 -MaxSamples 1).CounterSamples
    $committed = ($samples | Where-Object { $_.Path -like '*\memory\committed bytes' } | Select-Object -First 1).CookedValue
    $limit = ($samples | Where-Object { $_.Path -like '*\memory\commit limit' } | Select-Object -First 1).CookedValue
    if ($null -eq $committed -or $null -eq $limit) {
        throw 'Could not read Windows commit headroom.'
    }
    return [pscustomobject]@{
        FreePhysicalGB = [double]$os.FreePhysicalMemory / 1MB
        FreeCommitGB = [double]($limit - $committed) / 1GB
    }
}

function Start-BalancedRunner([int]$workers) {
    $env:PCAT_BALANCED_WORKERS = [string]$workers
    $out = Join-Path $here "balancedLR_${workers}worker_runner.stdout.log"
    $err = Join-Path $here "balancedLR_${workers}worker_runner.stderr.log"
    $process = Start-Process -FilePath $python -ArgumentList @('-u', $runner) `
        -WorkingDirectory $here -WindowStyle Hidden -RedirectStandardOutput $out `
        -RedirectStandardError $err -PassThru
    Write-WatchLog "Started $workers-worker runner, launcher PID $($process.Id)."
    return $process
}

function Stop-OldRun {
    $processes = Get-RunProcesses
    if ($processes.Count -eq 0) { throw 'No active balanced runner found; no switch was made.' }
    $runnerProcesses = @($processes | Where-Object { $_.CommandLine.Contains('run_full_balanced_lr.py') })
    $workerProcesses = @($processes | Where-Object { $_.CommandLine.Contains('main.py') })
    if ($runnerProcesses.Count -eq 0) { throw 'No parent balanced runner found; no switch was made.' }
    Write-WatchLog "Stopping old runner PIDs $($runnerProcesses.ProcessId -join ',') and worker PIDs $($workerProcesses.ProcessId -join ','); optimizer checkpoints are retained."
    foreach ($process in $runnerProcesses) {
        Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
    }
    foreach ($process in $workerProcesses) {
        Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
    }
    for ($attempt = 0; $attempt -lt 20; $attempt++) {
        if ((Get-RunProcesses).Count -eq 0) { break }
        Start-Sleep -Seconds 1
    }
    if ((Get-RunProcesses).Count -ne 0) {
        throw 'An old balanced Python process is still active; refusing to start duplicates.'
    }
    foreach ($process in $workerProcesses) {
        if ($process.CommandLine -match '--seeds\s+(\d+)') {
            $seed = $Matches[1]
            $source = Join-Path $here "balancedLR_seed$seed.stdout.log"
            if (Test-Path -LiteralPath $source) {
                Copy-Item -LiteralPath $source -Destination (Join-Path $here "balancedLR_seed${seed}_before_parallel.stdout.log") -Force
            }
        }
    }
}

if ($Probe) {
    $memory = Get-MemoryHeadroom
    $codeCount = @(Get-CimInstance Win32_Process -Filter "Name = 'Code.exe'").Count
    [pscustomobject]@{
        VSCodeProcesses = $codeCount
        FreePhysicalGB = [math]::Round($memory.FreePhysicalGB, 2)
        FreeCommitGB = [math]::Round($memory.FreeCommitGB, 2)
        RunProcesses = @((Get-RunProcesses)).Count
        Ready = ($codeCount -eq 0 -and $memory.FreePhysicalGB -ge 1.5 -and $memory.FreeCommitGB -ge 3)
    } | Format-List
    exit 0
}

try {
    Write-WatchLog 'Waiting for VS Code to close and at least 1.5 GB physical / 3 GB commit headroom.'
    $deadline = (Get-Date).AddHours(18)
    $closedAt = $null
    $readyCount = 0
    while ((Get-Date) -lt $deadline) {
        $status = Get-RunStatus
        if ($status -and $status.state -eq 'complete') {
            Write-WatchLog 'Balanced run already completed; no switch needed.'
            exit 0
        }
        $codeCount = @(Get-CimInstance Win32_Process -Filter "Name = 'Code.exe'").Count
        if ($codeCount -eq 0) {
            if ($null -eq $closedAt) { $closedAt = Get-Date }
            $memory = Get-MemoryHeadroom
            if ($memory.FreePhysicalGB -ge 1.5 -and $memory.FreeCommitGB -ge 3) {
                $readyCount++
            } else {
                $readyCount = 0
            }
            if ($readyCount -ge 2) {
                Write-WatchLog "VS Code closed; free physical $([math]::Round($memory.FreePhysicalGB,2)) GB, commit headroom $([math]::Round($memory.FreeCommitGB,2)) GB."
                break
            }
            if ((Get-Date) -gt $closedAt.AddMinutes(10)) {
                Write-WatchLog 'VS Code closed but memory stayed below the safe threshold; leaving the one-worker run unchanged.'
                exit 0
            }
        } else {
            $closedAt = $null
            $readyCount = 0
        }
        Start-Sleep -Seconds 15
    }
    if ((Get-Date) -ge $deadline) {
        Write-WatchLog 'Wait timed out; leaving the one-worker run unchanged.'
        exit 0
    }
    Stop-OldRun
    Start-BalancedRunner 2 | Out-Null
    Start-Sleep -Seconds 10
    $newStatus = Get-RunStatus
    if (-not $newStatus -or $newStatus.configuration.max_workers -ne 2) {
        if ((Get-RunProcesses).Count -eq 0) {
            Write-WatchLog 'Two-worker runner did not start; restarting in one-worker mode.'
            Start-BalancedRunner 1 | Out-Null
        } else {
            Write-WatchLog 'Two-worker Python process is alive; inspect the status file for startup progress.'
        }
    } else {
        Write-WatchLog 'Two-worker runner confirmed in status file.'
    }
    # An earlier two-worker attempt ran out of memory. If that happens again,
    # preserve its stderr and resume all unfinished seeds one at a time.
    while ($true) {
        Start-Sleep -Seconds 30
        $current = Get-RunStatus
        if (-not $current) { continue }
        if ($current.state -eq 'complete') {
            Write-WatchLog 'All five balanced seeds completed.'
            break
        }
        if ($current.state -ne 'failed') { continue }
        $errors = @(
            20..24 | ForEach-Object {
                $path = Join-Path $here "balancedLR_seed$_.stderr.log"
                if (Test-Path -LiteralPath $path) { Get-Content -LiteralPath $path -Raw }
            }
        ) -join "`n"
        if ($errors -notmatch '(?i)out of memory|not enough memory|paging file|memory allocation|DefaultCPUAllocator|bad_alloc') {
            Write-WatchLog 'Two-worker run failed for a reason other than memory; inspect status and stderr logs.'
            break
        }
        Write-WatchLog 'Two-worker run exhausted memory; returning to one worker from checkpoints.'
        foreach ($process in (Get-RunProcesses)) {
            Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
        }
        for ($attempt = 0; $attempt -lt 20; $attempt++) {
            if ((Get-RunProcesses).Count -eq 0) { break }
            Start-Sleep -Seconds 1
        }
        if ((Get-RunProcesses).Count -ne 0) {
            throw 'Parallel Python processes are still active; refusing to start a duplicate sequential run.'
        }
        foreach ($seed in 20..24) {
            $source = Join-Path $here "balancedLR_seed$seed.stderr.log"
            if ((Test-Path -LiteralPath $source) -and (Get-Item -LiteralPath $source).Length -gt 0) {
                Copy-Item -LiteralPath $source -Destination (Join-Path $here "balancedLR_seed${seed}_parallel_failed.stderr.log") -Force
            }
        }
        Start-BalancedRunner 1 | Out-Null
        break
    }
} catch {
    Write-WatchLog "Switch failed: $($_.Exception.Message)"
    if ((Get-RunProcesses).Count -eq 0) {
        Write-WatchLog 'Restarting from checkpoints with one worker.'
        Start-BalancedRunner 1 | Out-Null
    }
    exit 1
}
