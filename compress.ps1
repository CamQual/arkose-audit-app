Add-Type -AssemblyName System.Drawing
$imgPath = "C:\Users\Camille Goudard\Desktop\Projet_Dictaphone\background.jpg.jpeg"
$outPath = "C:\Users\Camille Goudard\Desktop\Projet_Dictaphone\background_small.jpg"
$img = [System.Drawing.Image]::FromFile($imgPath)
$newWidth = 1920
$newHeight = $img.Height * ($newWidth / $img.Width)
$bmp = New-Object System.Drawing.Bitmap($newWidth, [int]$newHeight)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.DrawImage($img, 0, 0, $newWidth, $newHeight)
$g.Dispose()
$img.Dispose()
$bmp.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Jpeg)
$bmp.Dispose()
