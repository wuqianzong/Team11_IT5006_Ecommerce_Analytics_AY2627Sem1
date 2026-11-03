# Submission format for the report (brief: 12 pt, single-spaced; body 15-20 pages excluding cover, references, appendices).
# A4, 2 cm margins, Times New Roman 12 pt body, tables 10 pt, wide charts 5.5 in, near-square charts 4.2 in,
# figure pairs in borderless tables at 3.3 in each (B-CR-52),
# cover on its own page, the review doc's own title/byline/note removed. Prints the body page range.
param([string]$Src, [string]$Docx, [string]$Pdf)
# Word needs full paths: resolve relative arguments against the current folder
$Docx = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Docx)
if ($Pdf) { $Pdf = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Pdf) }
$w = New-Object -ComObject Word.Application; $w.Visible = $false
try {
  Copy-Item $Src $Docx -Force
  $d = $w.Documents.Open($Docx)
  # drop everything above the cover heading (review doc title, byline, note)
  $first = $null
  foreach ($p in $d.Paragraphs) { if ($p.Range.Text.Trim() -like "Predicting delivery lead time*") { $first = $p; break } }
  $d.Range(0, $first.Range.Start).Delete() | Out-Null
  $ps = $d.PageSetup; $ps.PaperSize = 7; $cm = 28.35
  $ps.LeftMargin = 2*$cm; $ps.RightMargin = 2*$cm; $ps.TopMargin = 2*$cm; $ps.BottomMargin = 2*$cm
  $d.Content.Font.Name = "Times New Roman"
  foreach ($p in $d.Paragraphs) {
    $lvl = $p.OutlineLevel
    if ($lvl -eq 2) { $p.Range.Font.Size = 16 } elseif ($lvl -eq 3) { $p.Range.Font.Size = 13 } else { $p.Range.Font.Size = 12 }
    $p.Format.LineSpacingRule = 0
    $p.Format.SpaceBefore = [math]::Min($p.Format.SpaceBefore, 6); $p.Format.SpaceAfter = [math]::Min($p.Format.SpaceAfter, 6)
  }
  # figure pairs (B-CR-52): a borderless table holding pictures keeps 12 pt captions; its pictures are 3.3 in, side by side
  foreach ($t in $d.Tables) {
    if ($t.Range.InlineShapes.Count -gt 0) { $t.Range.ParagraphFormat.SpaceBefore = 0; $t.Range.ParagraphFormat.SpaceAfter = 6; continue }
    $t.Range.Font.Size = 10; $t.Range.ParagraphFormat.SpaceBefore = 0; $t.Range.ParagraphFormat.SpaceAfter = 0 }
  foreach ($s in $d.InlineShapes) { $s.LockAspectRatio = -1
    if ($s.Range.Information(12)) { $s.Width = 3.3*72; continue }
    $s.Width = 72; if (($s.Width / $s.Height) -lt 1.7) { $s.Width = 3.9*72 } else { $s.Width = 5.0*72 } }   # v2.4: 3.9 and 5.0 in (were 4.2 and 5.5) to keep the body within page 20
  foreach ($p in $d.Paragraphs) { if ($p.Range.Text.Trim() -eq "Executive summary") { $p.Format.PageBreakBefore = -1; break } }
  $d.Repaginate()
  $exec = 0; $last = 0; $refs = 0
  foreach ($p in $d.Paragraphs) {
    if ($p.OutlineLevel -ne 2) { continue }
    $t = $p.Range.Text.Trim()
    if ($t -eq "Executive summary") { $exec = $p.Range.Information(3) }
    if ($t -eq "References") {
      $refs = $p.Range.Information(3); $q = $p.Previous(1)
      while ($q.Range.Text.Trim().Length -eq 0) { $q = $q.Previous(1) }
      $last = $q.Range.Characters.Last.Information(3); break }
  }
  "body: pages {0}-{1} = {2} pages (references start p{3}); total {4}; pictures {5}" -f $exec, $last, ($last - $exec + 1), $refs, $d.ComputeStatistics(2), $d.InlineShapes.Count
  $d.Save()
  if ($Pdf) { $d.ExportAsFixedFormat($Pdf, 17) }
  $d.Close()
} finally { $w.Quit() }
