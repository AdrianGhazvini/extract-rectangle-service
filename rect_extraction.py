from flask import Flask, request, jsonify
import cv2
import numpy as np
import json, os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# port can be passed as env variable via docker-compose up command: FLASK_PORT=5002 docker-compose up
port = int(os.environ.get("FLASK_PORT", 5001))

# this function orders the points of a rectangle in the following order: top-left, top-right, bottom-left, bottom-right.
# the top two points are considered the two points with the lowest y-coordinates. The top of the rectangle is not based on the length of the edge.
def order_points(pts):
    # sort y-coordinates
    ySorted = pts[np.argsort(pts[:, 1]), :]

    # seperate top two and bottom two points
    topPoints = ySorted[:2, :]
    bottomPoints = ySorted[2:, :]

    # sort x-coordinates. leftmost point is the top-left corner
    topPoints = topPoints[np.argsort(topPoints[:, 0]), :]
    tl, tr = topPoints

    # same as above for the bottom two points
    bottomPoints = bottomPoints[np.argsort(bottomPoints[:, 0]), :]
    bl, br = bottomPoints

    # return order is top-left, top-right, bottom-left, bottom-right order
    return np.array([tl, tr, bl, br]).astype(int)

# this function sorts the individual points of the rectangles in the image from left to right based on the position of their top-left and bottom-left corners. Priority is given to rectangles higher in the image (lower y-axis value) if corners align on the x-axis.
def sort_rectangles(rectangles):
    rectangles.sort(key=lambda x: (x[1][0][0], x[1][0][1]))
    return rectangles

def extract_and_sort_rotated_rectangles(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if image is None:
        raise ValueError("Image not found")

    # apply a binary threshold to the image
    # 128 works here because pixels are either 0 (black) or 255 (white)
    _, binary_image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY_INV)

    # find contours
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    unsorted_rectangles = []

    # Extract rectangles using minArearect() and get corner points
    for contour in contours:
        rect = cv2.minAreaRect(contour)
        corners = cv2.boxPoints(rect)
        corners_ordered = order_points(corners)
        unsorted_rectangles.append((rect[0], corners_ordered))

    # sort, format and convert to JSON
    sorted_rectangles = sort_rectangles(unsorted_rectangles)
    rectangles_with_ids = [{"id": i, "coordinates": corners.tolist()} for i, (_, corners) in enumerate(sorted_rectangles)]
    rectangles_json = json.dumps(rectangles_with_ids, indent=4)

    return rectangles_json

@app.route('/extract-rect-coords', methods=['POST'])
def extract_rect_coords():
    if 'file' not in request.files:
        return jsonify(error="No file part"), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify(error="No selected file"), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join('/tmp', filename)

        try:
            # save using context manager
            with open(filepath, 'wb') as f:
                f.write(file.read())
            
            rectangles_json = extract_and_sort_rotated_rectangles(filepath)
            return rectangles_json
        except Exception as e:
            app.logger.error(f"Error processing file {filename}: {e}")
            return jsonify(error=str(e)), 500
        finally:
            # remove file in case of error
            if os.path.exists(filepath):
                os.remove(filepath)
    else:
        return jsonify(error="Invalid file type"), 400


@app.route('/extract-rect-coords-list', methods=['POST'])
def extract_rect_coords_list():
    if 'files' not in request.files:
        return jsonify(error="No file part"), 400

    files = request.files.getlist('files')
    
    if not files or len(files) == 0:
        return jsonify(error="No files provided"), 400

    results = []
    errors = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join('/tmp', filename)

            try:
                # save using context manager
                with open(filepath, 'wb') as f:
                    f.write(file.read())
                
                rectangles_json = extract_and_sort_rotated_rectangles(filepath)
                results.append(json.loads(rectangles_json))
            except Exception as e:
                errors.append({'file': filename, 'error': str(e)})
            finally:
                # remove file in case of error
                if os.path.exists(filepath):
                    os.remove(filepath)
        else:
            errors.append({'file': file.filename if file else 'unknown', 'error': 'Invalid file'})

    return jsonify({'results': results, 'errors': errors})

# ensure file is a png
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'png'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=port)
