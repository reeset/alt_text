## Dependencies ##

pip install python-dotenv
pip install boto3
pip install pybase64
pip install pillow

## Description ##

This is a sample script that demonstrates how to generate alt-text in batch.  The program works with image files, and will scale images automatically prior to sending data to aws for processing. 

## Usage ##
>> python .\alt_text_testing.py -s .\samples\sample_output\output.txt -d .\samples\images\ -llm sonnet3.52

Arguments:
 -s: Save file for output [required]
 -d: folder to process [required]
 -llm: defined llm in bedrock (few have been added) [optional - default is sonnet3.51]
 -r: generates a random sample of 500 images

 ## Samples ##
 Sample images and a sample output file run using Sonnet 3.5 V2 is in the samples directory
