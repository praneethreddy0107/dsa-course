# Initialize an empty list to store the marks
marks = []

# Initialize variables for sum and count
total_sum = 0
count = 0

# Loop to read the marks
while True:
    # Ask for user input
    mark = input("Enter the mark for a subject (or type 'done' to finish): ")
    
    # Check if the user wants to finish input
    if mark.lower() == 'done':
        break
    
    try:
        # Convert the input to a float and add it to the list
        mark = float(mark)
        marks.append(mark)
        
        # Update the sum and count
        total_sum += mark
        count += 1
    except ValueError:
        # If the input is not a number, show an error message
        print("Please enter a valid number or 'done' to finish.")

# Calculate the average if there are any marks
if count > 0:
    average = total_sum / count
else:
    average = 0

# Print the results
print(f"\nTotal marks: {total_sum}")
print(f"Average marks: {average:.2f}")
print(f"\ marks: {marks}")
