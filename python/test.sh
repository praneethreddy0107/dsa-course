#!/bin/bash

# Initialize sum and count variables
total_sum=0
count=0

# Function to check if the input is a valid number
is_number() {
    local s="$1"
    [ "$s" -eq "$s" ] 2>/dev/null
}

# Loop to read the marks
while true; do
    # Ask for user input
    read -p "Enter the mark for a subject (or type 'done' to finish): " mark
    
    # Check if the user wants to finish input
    if [ "$mark" = "done" ]; then
        break
    fi
    
    # Check if the input is a valid number
    if is_number "$mark"; then
        # Add the mark to the total sum and increment count
        total_sum=$((total_sum + mark))
        count=$((count + 1))
    else
        # If the input is not a number, show an error message
        echo "Please enter a valid number or 'done' to finish."
    fi
done

# Calculate the average if there are any marks
if [ "$count" -gt 0 ]; then
    average=$(echo "scale=2; $total_sum / $count" | bc)
else
    average=0
fi

# Print the results
echo
echo "Total marks: $total_sum"
echo "Average marks: $average"
# ===========================
# ============================

    read -p "enter the name " name
    if [ "$name"="praneeth" ]; then 
    echo "lenfgth ok"
    else 
    echo "not ok"
    fi