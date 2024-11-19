import pandas as pd
import numpy as np

input_file = r''
df = pd.read_excel(input_file)

maxi = df.iloc[0, 2:].astype(float)  
weightage = df.iloc[1, 2:].astype(float) / 100 

df = df.drop([0, 1]).reset_index(drop=True)

df.iloc[:, 2:] = df.iloc[:, 2:].apply(pd.to_numeric)

# Calculate weighted total 

df['Grand Total/100'] = sum(
    (df[col] / maxi[col] * weightage[col] * 100) for col in maxi.index
)

# Define grading criteria based on 'Grand Total/100'

df['Grade'] = df['Grand Total/100'].apply(assign_grade)

# Define 'Total Students' and count students in each grade for extra columns
total_students = len(df)
grade_counts = df['Grade'].value_counts().reindex(['AA', 'AB', 'BB', 'BC', 'CC', 'CD', 'DD', 'F'], fill_value=0).astype(int)
df['Total Students'] = total_students

df['grade'] = df['Grade']  # Assuming same grade for simplicity
df['old iapc reco'] = grade_counts[df['Grade']].values
df['Counts'] = grade_counts[df['Grade']].values * 1.02 
df['Round'] = np.round(df['Counts'])
df['Count verified'] = df['Round'].astype(int)

# Sort the dataframe by roll number and by Total
df_roll_sorted = df.sort_values(by='Roll')
df_marks_sorted = df.sort_values(by='Grand Total/100', ascending=False)

# Final Output containing two sheets in a single excel file
output_excel_file = 'output_combined.xlsx'
with pd.ExcelWriter(output_excel_file) as writer:
    df_roll_sorted.to_excel(writer, sheet_name='Sorted by Roll Number', index=False)
    df_marks_sorted.to_excel(writer, sheet_name='Sorted by Marks', index=False)

print("Combined output file generated successfully: output_combined.xlsx")