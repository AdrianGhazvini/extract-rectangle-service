# Extract Rectangle Service

## Overview

Extract Rectangle Service is a Flask-based microservice that processes `.png` images to identify and extract the coordinates of black rectangular shapes. The service is designed to handle images containing only black and white pixels, where the rectangles are black. It returns a JSON list of objects, each containing a unique identifier and the coordinates of the rectangle corners.

### Notes on Image Processing

- The rectangles are sorted from left to right based on the position of their top-left and bottom-left corners. Priority is given to rectangles higher in the image (lower y-axis value) if corners align on the x-axis.
- The service processes images in memory and removes them post-processing to handle concurrent requests efficiently and avoid scalability concerns.
- The service only works with the provided black and white images oulined in the code challende instructions so fixed threshold of 128 is used.

## Requirements

- **Docker** The primary requirement is Docker, as it encapsulates all other dependencies within the container. Ensure you have Docker and Docker Compose installed for managing the container.

**note:** If you're not using Docker and prefer a manual setup, you would need the following:
- Python 3.8
- Flask, OpenCV (opencv-python-headless), Numpy, Requests (included in `requirements.txt`)

## Installation

### Using Docker:

1. **Install Docker:**
   - [Docker Engine for Linux](https://docs.docker.com/engine/install/)
   - Docker Desktop for [Mac](https://docs.docker.com/desktop/install/mac-install/), [Windows](https://docs.docker.com/desktop/install/windows-install/), [Linux](https://docs.docker.com/desktop/install/linux-install/)

2. **Clone the Repository:**
   - You can find instructions on how to clone a GitHub repository [here](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) or use one of the two methods below
   - Using Git:
     ```
     git clone https://github.com/your-repository/extract-rectangle-service.git
     ```
   - Alternatively, download and unzip the repository from GitHub.

4. **Navigate to the Project Directory:**
   - Open the project directory in Terminal for Mac and Linux. For Windows ouse Powershell or Command Prompt.

5. **Build and Run the Docker Container:**
  ```
  docker-compose up --build
  ```
or to starts the container in the background
  ```
  docker-compose up --build -d
  ```
**note:** The default port set for this application is 5001 due to port 5000 being used by some the control center in some iOS versions. If you need to use a different port, you can specify a custom port by setting the FLASK_PORT environment variable before the docker-compose command 
  ```
  FLASK_PORT=6000 docker-compose up --build -d
  ```

## Usage

The microservice provides two endpoints:

- `/extract-rect-coords`: Accepts a single image and returns the coordinates of rectangles.
- `/extract-rect-coords-list`: Accepts a list of images and returns coordinates for each.

### Sending Requests

- **Single Image:**
  ```
  curl -F "file=@./test_images/simple.png" http://localhost:5001/extract-rect-coords
  ```

- **Multiple Images:**
  ```
  curl -X POST -F "files=@./test_images/simple.png" -F "files=@./test_images/rotated.png" http://localhost:5001/extract-rect-coords-list
  ```
- **Using Postman:**
  
 Postman can also be used for sending requests, you can find detailed instructions on how to set up and use Postman for API requests [here](https://learning.postman.com/docs/introduction/overview/).

## Testing

### Using Docker:

- **Run Tests:**
  ```
  docker-compose run test_service
  ```

### Without Docker:
  ```
  cd tests
  ```
- **Run Unit Tests:**
  ```
  python -m unittest test_microservice.py
  ```
- **Navigate to the Tests Directory:**

## Notes for Windows Users

- If prompted by Windows Defender Firewall, allow access to ensure proper functioning of the service.
- In case of port conflicts, modify the port mapping in the Docker command.

## Cleanup

- **Remove Docker Container:**
After testing, you can remove the Docker container using:

  ```
  docker-compose down

  ```
## Sample Outputs
**sample output for single image endpoint (/extract-rect-coords):**

[

  {"id": 0, "coordinates": [[75, 56], [124, 56], [75, 455], [124, 455]]},
  
  {"id": 1, "coordinates": [[231, 56], [280, 56], [231, 455], [280, 455]]},
  
  {"id": 2, "coordinates": [[387, 56], [436, 56], [387, 455], [436, 455]]}
  
]

**sample output for single image endpoint (/extract-rect-coords-list):**

{ "errors":[],

"results": [

[{"coordinates":[[75,56],[124,56],[75,455],[124,455]],"id":0},

{"coordinates":[[231,56],[280,56],[231,455],[280,455]],"id":1},

{"coordinates":[[387,56],[436,56],[387,455],[436,455]],"id":2}],

[{"coordinates":[[107,51],[156,60],[46,396],[96,405]],"id":0},

{"coordinates":[[261,78],[310,87],[200,423],[249,432]],"id":1},

{"coordinates":[[414,105],[464,114],[354,450],[403,459]],"id":2}]

]}

