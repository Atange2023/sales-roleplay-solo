param([string]$Voice = 'Microsoft Huihui Desktop')

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$root = Split-Path -Parent $PSScriptRoot
$entries = (Get-Content -LiteralPath (Join-Path $root 'assets\fixed-lines.json') -Raw -Encoding UTF8 | ConvertFrom-Json).entries
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$available = @($synth.GetInstalledVoices() | Where-Object Enabled | ForEach-Object { $_.VoiceInfo.Name })
if ($available -contains $Voice) { $synth.SelectVoice($Voice) }
foreach ($entry in $entries) {
    $mp3 = Join-Path $root ($entry.file -replace '/', '\')
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $mp3) | Out-Null
    $wav = [System.IO.Path]::ChangeExtension($mp3, '.wav')
    $synth.Rate = [int]$entry.generation.rate
    $synth.SetOutputToWaveFile($wav)
    $synth.Speak([string]$entry.spoken_text)
    $synth.SetOutputToNull()
    & ffmpeg -y -loglevel error -i $wav -codec:a libmp3lame -b:a 64k $mp3
    if ($LASTEXITCODE -ne 0) { throw "ffmpeg failed for $mp3" }
    Remove-Item -LiteralPath $wav -Force
}
$synth.Dispose()
Write-Output ("generated {0} fixed MP3 files" -f $entries.Count)