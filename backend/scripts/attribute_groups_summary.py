import pandas as pd

# Load the Excel file
file_path = "filtered data.xlsx"  # Update with your file path if needed
df = pd.read_excel(file_path, sheet_name='Sheet1')

# Group by 'IM GUI Item Attribute Set' and count unique 'IM / Load Sheet (FUSE) XML Name'
grouped_counts = df.groupby('IM GUI Item Attribute Set')['IM / Load Sheet (FUSE) XML Name'].nunique().reset_index()

# Rename columns for clarity
grouped_counts.columns = ['IM GUI Item Attribute Set', 'Unique XML Name Count']

# Save to CSV (optional)
grouped_counts.to_csv('xml_name_counts_by_attribute_set.csv', index=False)

# Print the result
print(grouped_counts)
