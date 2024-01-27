import unittest, json, os, requests

class MicroserviceTest(unittest.TestCase):
    port = os.getenv("TEST_PORT", "5001")
    # check if running in docker
    if os.path.exists('/usr/src/app/coordinates.json'):
        # Docker paths
        EXPECTED_OUTPUTS_FILE = '/usr/src/app/coordinates.json'
        TEST_IMAGES_DIR = '/usr/src/app/test_images'
        URL = f"http://host.docker.internal:{port}/extract-rect-coords"
    else:
        # if not in docker use local paths
        EXPECTED_OUTPUTS_FILE = './coordinates.json'
        TEST_IMAGES_DIR = '../test_images'
        URL = f"http://localhost:{port}/extract-rect-coords"
   
    @classmethod
    def setUpClass(cls):
        with open(cls.EXPECTED_OUTPUTS_FILE) as f:
            cls.expected_outputs = json.load(f)

    def perform_image_test(self, image_name):
        expected_output = next((item for item in self.expected_outputs if item["name"] == image_name), None)
        self.assertIsNotNone(expected_output, "Expected output not found for image")

        with open(os.path.join(self.TEST_IMAGES_DIR, image_name), 'rb') as img:
            files = {'file': img}
            response = requests.post(self.URL, files=files)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), expected_output["output"])


    def test_rotated_left(self):
        self.perform_image_test('rotated_left.png')

    def test_horizontal(self):
        self.perform_image_test('horizontal.png')

    def test_rotated(self):
        self.perform_image_test('rotated.png')

    def test_simple(self):
        self.perform_image_test('simple.png')

    def test_black(self):
        self.perform_image_test('black.png')

    def test_white(self):
        self.perform_image_test('white.png')

    def test_invalid_file_format(self):
        with open(os.path.join(self.TEST_IMAGES_DIR, 'simple.jpg'), 'rb') as img:
            files = {'file': img}
            response = requests.post(self.URL, files=files)
            self.assertNotEqual(response.status_code, 200)

    def test_corrupted_file(self):
        with open(os.path.join(self.TEST_IMAGES_DIR, 'simple_corrupted.png'), 'rb') as img:
            files = {'file': img}
            response = requests.post(self.URL, files=files)
            self.assertNotEqual(response.status_code, 200)

    def test_rectangles_on_all_edges(self):
        self.perform_image_test('rectangles_on_all_edges.png')

    def test_rectangle_on_top_left_edges(self):
        self.perform_image_test('rectangle_on_top_left_edges.png')

    def test_rectangle_on_left_edge(self):
        self.perform_image_test('rectangle_on_left_edge.png')

    def test_rectangle_on_left_top_bottom_edges(self):
        self.perform_image_test('rectangle_on_left_top_bottom_edges.png')

if __name__ == '__main__':
    unittest.main()
