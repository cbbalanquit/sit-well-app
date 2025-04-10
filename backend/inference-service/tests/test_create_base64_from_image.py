import base64

# Convert image to base64
with open("./test_images/improper-chair-sit-3.jpg", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
print(encoded_string)