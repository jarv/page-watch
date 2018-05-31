#!/bin/bash
#

#  The following variables must be set in the environment

#  CAP_FNAME                    - file name of the capture file
#  CAP_FNAME_RESIZED            - file name of the capture file
#  CAP_HIGHLIGHT_FNAME          - file name of the highlighted file that will be generated
#  LAST_CAP_FNAME               - file name of the previous capture
#  LAST_CAP_FNAME_RESIZED       - file name of the previous capture
#  LAST_CAP_HIGHLIGHT_FNAME     - file name of the highlighted file that will be generated
#  MASK_FNAME                   - file name for the intermediate mask file that is applied to the original capture
#  MASK_BLUR_FNAME              - file name for the blurred mask file
#  MASK_BLUR_MONOCHROME_FNAME   - file name for the final mask that is applied


for env_var in CAP_FNAME CAP_FNAME_RESIZED CAP_HIGHLIGHT_FNAME LAST_CAP_FNAME LAST_CAP_FNAME_RESIZED LAST_CAP_HIGHLIGHT_FNAME MASK_FNAME MASK_BLUR_FNAME MASK_BLUR_MONOCHROME_FNAME; do
    if [[ -z ${!env_var} ]]; then
        echo "Environment not correct for script!"
        env
        exit 1
    fi
done

set -eux

echo "creating MASK_FNAME"
compare -dissimilarity-threshold 1 -fuzz 20% "$LAST_CAP_FNAME_RESIZED" "$CAP_FNAME_RESIZED" -subimage-search  -compose Src -highlight-color White -lowlight-color Black "$MASK_FNAME"
echo "bluring MASK_FNAME"
convert "$MASK_FNAME" -blur 0x5 "$MASK_BLUR_FNAME"
echo "converting MASK_FNAME"
convert "$MASK_BLUR_FNAME" -colorspace gray -auto-level -threshold 0% "$MASK_BLUR_MONOCHROME_FNAME"
echo "blending"
composite -blend 80 "$LAST_CAP_FNAME_RESIZED" "$MASK_BLUR_MONOCHROME_FNAME" "$CAP_HIGHLIGHT_FNAME"
composite -blend 80 "$CAP_FNAME_RESIZED" "$MASK_BLUR_MONOCHROME_FNAME" "$LAST_CAP_HIGHLIGHT_FNAME"
