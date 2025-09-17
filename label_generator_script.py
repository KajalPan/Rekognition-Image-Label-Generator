# Importing the necessary libraries
import boto3
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import io

# Get the Amazon Rekognition Client initialized
def initialize_rekognition_client():
    return boto3.client('rekognition')

# Use boto3 as part of the AWS SDK to pull images from Amazon S3
def fetch_image_from_s3(bucket_name, image_key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=image_key)
    return response['Body'].read()

# This function produces the labels from the client set up earlier
def detect_labels(client, bucket_name, image_key):
    response = client.detect_labels(
        Image={'S3Object': {'Bucket': bucket_name, 'Name': image_key}},
        MaxLabels=10,
        MinConfidence=70
    )
    return response['Labels']

# The fun part which uses draws red bounding boxes around the labels Rekognition detects
def draw_bounding_boxes(image_bytes, labels):
    image = Image.open(io.BytesIO(image_bytes))
    draw = ImageDraw.Draw(image)

    for label in labels:
        if 'Instances' in label:
            for instance in label['Instances']:
                if 'BoundingBox' in instance:
                    box = instance['BoundingBox']
                    width, height = image.size
                    left = box['Left'] * width
                    top = box['Top'] * height
                    right = left + box['Width'] * width
                    bottom = top + box['Height'] * height
                    # Draw the bounding box
                    draw.rectangle([left, top, right, bottom], outline="red", width=3)
                    draw.text((left, top), label['Name'], fill="red")
    return image

def main():
    # S3 bucket and image configuration
    bucket_name = "kaj-image-label-generator"
    # Call the Amazon Rekognition client to initialize it
    rekognition_client = initialize_rekognition_client()
    images = ["1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg", "6.jpg"]   

    # Loop through all of my images
    for image in images:
        image_key = image
        # Fetch Image from S3
        image_bytes = fetch_image_from_s3(bucket_name, image_key)

        # Detect Labels
        labels = detect_labels(rekognition_client, bucket_name, image_key)
        print("Detected Labels:")
        for label in labels:
            print(f"{label['Name']} - Confidence: {label['Confidence']:.2f}%")

        # Draw Bounding Boxes
        labeled_image = draw_bounding_boxes(image_bytes, labels)

        # Display Image with Matplotlib
        plt.figure(figsize=(10, 8))
        plt.imshow(labeled_image)
        plt.axis('off')
        plt.show()  

if __name__ == "__main__":
    main()