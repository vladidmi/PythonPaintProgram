import openpyxl


def read_excel_file(filename):
    # Load the workbook
    workbook = openpyxl.load_workbook(filename)
    # Get the specific worksheet
    worksheet = workbook["Arbeitsschritte"]
    # Initialize the dictionary to store the data
    data = {}
    # Iterate through the rows
    for row in worksheet.iter_rows():
        # Get the key from the first column
        key = row[0].value
        if key == "Strukturtyp":
            continue
        # Initialize the dictionary for the current row
        row_data = {}
        # Iterate through the remaining columns
        for cell in row[1:]:
            # Get the value and color of the cell
            value = cell.value
            if value == None:
                continue
            color = cell.fill.start_color.index
            # Add the data to the dictionary for the current row
            row_data[value] = color
        # Add the data for the current row to the main dictionary
        data[key] = row_data
    # Return the dictionary
    return data


data = read_excel_file(
    r"D:\projects\github\test_github\PythonPaintProgram\projekt_info.xlsx"
)
print(data)
