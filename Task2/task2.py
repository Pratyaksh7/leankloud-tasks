import csv
with open('Student_marks_list.csv', 'r') as file:
    rows = csv.reader(file, delimiter=',')
    new_rows = [row for row in rows]     # Complexity O(n) n-> number of rows

    names = []
    maths = []
    biology = []
    english = []
    physics = []
    chemistry = []
    hindi = []
    average = []

    for line in new_rows[1:]:   # Complexity O(nm)  m-> number of columns
        names.append(line[0])
        maths.append(int(line[1]))
        biology.append(int(line[2]))
        english.append(int(line[3]))
        physics.append(int(line[4]))
        chemistry.append(int(line[5]))
        hindi.append(int(line[6]))

    for i in range(len(maths)):     # Complexity O(n)
        total = 0
        total = total + maths[i] + biology[i] + english[i] + physics[i] + chemistry[i] + hindi[i]
        average.append(total/6)

    # Overall Complexity: 2O(n) + O(nm) = O(n) + O(nm)

    print("Topper in Maths is", names[maths.index(max(maths))])
    print("Topper in Biology is", names[biology.index(max(biology))])
    print("Topper in English is", names[english.index(max(english))])
    print("Topper in Physics is", names[physics.index(max(physics))])
    print("Topper in chemistry is", names[chemistry.index(max(chemistry))])
    print("Topper in Hindi is", names[hindi.index(max(hindi))])
    beststudents = sorted(zip(average, names), reverse=True)[:3]   # it will sort the pair in descending order and then we took the first three students
    print("Best students in the class are {} first rank, {} second rank, {} third rank ".format(beststudents[0][1], beststudents[1][1], beststudents[2][1]))
