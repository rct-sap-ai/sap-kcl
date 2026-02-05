from auto_sap.classes.auto_code_api_classes import auto_code_api



api_prod = auto_code_api(dev = False)
api_dev = auto_code_api(dev = True)


variable_types = api_prod.get_("variable_type/")
print(variable_types)

# api_dev.post_methods(methods)

def transfer_to_dev(item_list, url_suffix):
    for item in item_list:
        # 1. Remove the original ID so DEV creates a new one
        # If your DEV endpoint uses GetOrCreate, it will use the 'slug' or 'title'
        item_data = item.copy()
        item_data.pop('id', None) 
        
        # 2. Handle nested method_arguments if they exist
        # If method_arguments is an empty list [], most APIs handle it fine.
        
        try:
            print(f"Transferring: {item_data.get('title')}...")
            api_dev.post_(item_data, url_suffix)
        except Exception as e:
            print(f"Failed to post {item_data.get('title')}: {e}")

# Call it with your list
variable_types = api_prod.get_("variable_type/")
print(variable_types)
#transfer_to_dev(variable_types, "variable_type/")


methods = api_prod.get_methods()
print("Methods from PROD API:")
print(methods)

allowed_keys = ['title', 'slug', 'stata_code', 'model_name']
# Create a new dictionary containing ONLY the allowed keys
cleaned_methods = [
    {k: v for k, v in m.items() if k in allowed_keys}
    for m in methods
]
transfer_to_dev(cleaned_methods, "method/") 