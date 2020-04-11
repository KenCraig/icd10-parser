# I don't use this, but if you'd like to build an image for running this, start here

# We simply inherit the Python 3 image. This image does
# not particularly care what OS runs underneath
FROM python:3.7-slim

# Set an environment variable with the directory
# where we'll be running the app
ENV APP /app

# Create the directory and instruct Docker to operate
# from there from now on
#RUN mkdir -p $APP/txt $APP/xml
RUN mkdir -p $APP
WORKDIR $APP

# Copy the requirements file in order to install
# Python dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# We copy the rest of the codebase into the image
COPY . .

#CMD [ "python", "icd10parse.py", "tmp/icd10cm_tabular_2020.xml", "tmp/icd10cm_order_2020.txt" ]
CMD [ "bash" ]
