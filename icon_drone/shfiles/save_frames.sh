#!/bin/bash

BASE_DIR="$HOME/ELEC491_TL101/icon_drone/frames"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FRAME_DIR="$BASE_DIR/frames_$TIMESTAMP"

mkdir -p "$FRAME_DIR"

# High quality capture settings
RESOLUTION="1280x720"
FRAME_RATE="30"
DEVICE="/dev/video6"

echo "=== Frame Capture Mode (High Quality, 30 FPS) ==="
echo "- Resolution: $RESOLUTION"
echo "- Frame rate: $FRAME_RATE"
echo "- Saving JPEG frames to: $FRAME_DIR"
echo "Press 'r' to start capturing, 'q' to stop."

recording=false
pid=0

while true; do
    # read -rsn1 key
    # if [[ $key == "r" && $recording == false ]]; then
        echo "Capturing high-quality frames..."
        recording=true

        # Disable FFmpeg keyboard input
        ffmpeg -f v4l2 -input_format mjpeg -framerate "$FRAME_RATE" -video_size "$RESOLUTION" \
            -i "$DEVICE" -q:v 2 "$FRAME_DIR/frame_%04d.jpg" < /dev/null &
        pid=$!

    # elif [[ $key == "q" && $recording == true ]]; then
    #    echo "Stopping capture..."
    #    kill $pid 2>/dev/null
    #    wait $pid 2>/dev/null
    #    recording=false

    #    echo "Frames saved to: $FRAME_DIR"
    #    exit 0
    # fi
done

