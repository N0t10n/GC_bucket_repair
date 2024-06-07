#!/bin/bash

# Define the bucket path
BUCKET_PATH="gs://data-tappx-us-2/ssp/raw"

# Iterate over each network directory
for network in afm apn apnd2 apnvd cb cbv cte ctn imrtb imrtbv lp lpn lpv otgd pu puctv pur purv purv2 rbx rbxp rbxv sas sasdrtb sasn saspd saspv sasvrtb unrld unrlv; do
    # Construct the new network directory name
    network_dir="net=$network"
    # Iterate over each date directory within the network directory
    for date_dir in $(gsutil ls "$BUCKET_PATH/historico/$network_dir"); do
        # Extract the date from the directory path
        date_dir=$(basename "$date_dir")

        # Rename the date directory
        if [ $date_dir == "rqDate=2024-04-29" ]; then
            OLD_PATH="$BUCKET_PATH/historico/$network_dir/$date_dir"
            NEW_PATH="$BUCKET_PATH/quarentine/$network_dir/$date_dir"

            object_count=$(gsutil ls -l $OLD_PATH | wc -l)
            # If there are no objects, skip to the next iteration
            if [ $object_count -eq 0 ]; then
                echo "$OLD_PATH has $object_count objects"
                continue
            fi

            gsutil -m mv "$OLD_PATH" "$NEW_PATH"
            gsutil rm -r "$OLD_PATH/"
        fi
    done
done
