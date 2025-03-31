name= input("enter the student name: ")
print(name)
marks=[]
total_sum = 0
count = 0
while True :
    mark = input("Enter the mark for a subject (or type 'done' to finish): ")
    if mark.lower() == 'done':
        break 
    try :
        mark = float(mark)
       # marks.append(mark)
        # Update the sum and count
        total_sum += mark
        count += 1
    except ValueError :
        print("Error")
if count > 0 :
    average = total_sum / count
else :
    average=0
# Print the results
print(f"\nTotal marks: {total_sum}")
print(f"Average marks: {average:.2f}")