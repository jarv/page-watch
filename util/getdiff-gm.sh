set -e

echo "fetching first"
#cutycapt --url=\'${1}\' --out=one.png
wkhtmltoimage $1 one.png
echo "sleeping 5"
sleep 20
echo "fetching second"
#cutycapt --url=\'${1}\' --out=two.png
wkhtmltoimage $1 two.png

one_height=$(identify -quiet -format "%H" one.png)
two_height=$(identify -quiet -format "%H" two.png)

if (( $one_height > $two_height )); then
    echo "resizing height of one to match two"
    gm convert -crop x$(identify -quiet -format "%H" two.png)+0+0 -page x$(identify -quiet -format "%H" two.png)+0+0 one.png one-0.png
    mv one-0.png one.png
elif (( $two_height > $one_height )); then
    echo "resizing height of two to match one"
    gm convert -crop x$(identify -quiet -format "%H" one.png)+0+0 -page x$(identify -quiet -format "%H" one.png)+0+0 two.png  two-0.png
    mv two-0.png two.png
fi

one_width=$(identify -quiet -format "%W" one.png)
two_width=$(identify -quiet -format "%W" two.png)

if (( $one_width > $two_width )); then
    echo "resizing width of one to match two"
    gm convert -crop x$(identify -quiet -format "%W" two.png)+0+0 -page x$(identify -quiet -format "%W" two.png)+0+0 one.png one-0.png
    mv one-0.png one.png
elif (( $two_width > $one_width )); then
    echo "resizing width of two to match one"
    gm convert -crop x$(identify -quiet -format "%W" one.png)+0+0 -page x$(identify -quiet -format "%W" one.png)+0+0 two.png  two-0.png
    mv two-0.png two.png
fi

one_height=$(identify -quiet -format "%H" one.png)
two_height=$(identify -quiet -format "%H" two.png)

if (( $one_height > 2048 )); then
    echo "one_height too tall, resizing"
    gm convert -resize x2048+0+0 -page x2048+0+0 one.png one-0.png
    mv one-0.png one.png
fi

if (( $two_height > 2048 )); then
    echo "two_height too tall, resizing"
    gm convert -resize x2048+0+0 -page x2048+0+0 two.png two-0.png
    mv two-0.png two.png
fi

echo "creating mask"
gm compare  one.png two.png  mask.png
echo "bluring mask"
gm convert mask.png -blur 0x5 mask-blur.png
echo "converting mask"
convert mask-blur.png -colorspace gray -auto-level -threshold 0% mask-blur-monochrome.png
echo "blending"
gm composite -dissolve 80 one.png mask-blur-monochrome.png one-highlighted.png
gm composite -dissolve 80 two.png mask-blur-monochrome.png two-highlighted.png

