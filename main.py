import os
import requests
import copy
import csv 
import synonymes

al_moufta7 = "2b10OOVqKH3mbCUeCnWRXXqc5"
dataset_path = 'dataset'
output_path = 'output'


# Define your parameters
project = "all"
organs = ["auto"]  # Organs corresponding to the images
include_related_images = False  # Optional, set to True if you want related images
no_reject = False  # Optional, disable rejection class match if needed
nb_results = 5  # Number of species to return
lang = "en"  # Language setting
type_model = "kt"  # Model type: 'kt' for new, 'legacy' for old
api_key = al_moufta7 

# Set the API endpoint URL
url = f"https://my-api.plantnet.org/v2/identify/{project}"


def list_folders():
    # List all folders in the dataset and count the number of files in each
    folders = [folder_name for folder_name in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, folder_name))]
    
    print("Available Folders:")
    for idx, folder_name in enumerate(folders):
        folder_path = os.path.join(dataset_path, folder_name)
        
        # Count the number of files in the folder
        num_files = len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])
        
        # Display folder name with number of files
        print(f"{idx}: {folder_name} ({num_files} files)")
    
    return folders




def fill_dictionary(selected_folder):
    dataset = []
    folder_path = os.path.join(dataset_path, selected_folder)

    # Iterate through each image file in the selected folder
    c = 0
    dirs = os.listdir(folder_path)
    for image_name in dirs:
        print(f'Progress: {c+1}/{len(dirs)} ')
        image_path = os.path.join(folder_path, image_name)

        dataset.append(api_call(image_path, selected_folder,image_name))
        c += 1
        
    return dataset



def api_call(image_path, folder_name, image_name):
    # Set the form data and query parameters
    data = {
        "organs": organs,
    }

    params = {
        "include-related-images": str(include_related_images).lower(),
        "no-reject": str(no_reject).lower(),
        "nb-results": nb_results,
        "lang": lang,
        "type": type_model,
        "api-key": api_key,
    }
    
    # Open the image file in binary mode
    # Set the files for the request, the key 'file' depends on your API
    files = {
            "images": (image_path, open(image_path, 'rb'), 'image/jpg'),  # Make sure the image is in binary mode ('rb')
        }

    # Send the POST request
    response = requests.post(url, files=files, data=data, params=params)
    # Check the response status code and output the result
    if response.status_code == 200:
        # Check if the response contains valid JSON
        if response.headers.get('Content-Type') == 'application/json; charset=utf-8':
            data = response.json()  # Safely parse JSON
            """print(data["results"][0]["species"]["scientificNameWithoutAuthor"])"""
            return (data, image_name)
        else:
            print("Non-JSON response received:", response.text)
    else:
        print(f"Error: {response.status_code}, {response.text}")

    return None




def process_dataset(dataset, folder_name):
    genus = folder_name.split(' ')[0]
    species = folder_name
    print(genus)
    print(species)
    output_element = [folder_name, "image_name", False, False, 0, "name_in_first", 0.0, 0.0]
    output_list = []
    for e in dataset:
        output_element[1] = e[1]
        output_element[2] = species == (e[0]["results"][0]["species"]["scientificNameWithoutAuthor"]) or (e[0]["results"][0]["species"]["scientificNameWithoutAuthor"] in synonymes.synonymes[species])
        output_element[3] = genus == e[0]["results"][0]["species"]["genus"]["scientificNameWithoutAuthor"]
        output_element[5] = e[0]["results"][0]["species"]["scientificNameWithoutAuthor"]
        output_element[6] = e[0]["results"][0]["score"]
        c = 0
        for result in e[0]["results"]:
            c += 1
            if (result["species"]["scientificNameWithoutAuthor"] == species) or (result["species"]["scientificNameWithoutAuthor"] in synonymes.synonymes[species]):
                break
            elif c == 5:
                c = 0
        

        if c != 0:
            output_element[4] = 6 - c
        else: output_element[4] = 0

        if c != 0:
            output_element[7] = e[0]["results"][c-1]["score"]
        else:
            output_element[7] = 0


        output_list.append(copy.deepcopy(output_element))
    return output_list



def serialize(processed_data, output, selected_folder):
    selected_folder = selected_folder + ".csv"
    filepath = os.path.join(output, selected_folder)
    file = open(filepath, 'w', newline='')

    writer = csv.writer(file)
    writer.writerows(processed_data)

    print(f"Data has been written to {selected_folder}")
    return True





def driver(output):
    # List available folders
    folders = list_folders()

    # Ask the user to select a folder by number
    try:
        selected_number = int(input("Enter the number of the folder you want to process: "))
        if selected_number < 0 or selected_number >= len(folders):
            raise ValueError("Invalid selection")
        selected_folder = folders[selected_number]

        # Process the selected folder
        dataset = fill_dictionary(selected_folder)

    except ValueError as e:
        print(f"Error: {e}")
    processed_dataset = process_dataset(dataset, selected_folder)  
    print(processed_dataset)
    return serialize(processed_dataset, output, selected_folder)


driver(output_path)