from utils import *
from flask import Blueprint,render_template,request,jsonify
import tensorflow as tf
import base64
import io
from PIL import Image
views = Blueprint("views",__name__)
 
ocr_model = None  
ocr_sub_model = None


MODEL_PATH = 'models/ocr_big_1.h5'
SUB_MODEL_PATH= 'models/ocr_new_1.h5'

@views.route('/',methods=['GET','POST'])
def index():  
    global ocr_model
    global ocr_sub_model 

    if request.method == 'POST':
        data = request.json['image']
        head, data = data.split(',', 1)
        image_data = base64.b64decode(data)
    
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        
        processed_image = np.array(image)
        
        if not ocr_model:
            ocr_model =  tf.keras.models.load_model(MODEL_PATH)
        if not ocr_sub_model:
            ocr_sub_model = tf.keras.models.load_model(SUB_MODEL_PATH)


        detected_contours,output_image, coords = get_results(processed_image)
        output_string = ""
        for i in range(len(detected_contours)):
            predicted_char = predict(ocr_model, ocr_sub_model,detected_contours[i],mappings)

            if predicted_char == '0':
                output_string += 'O'
                cv2.putText(output_image, 'O', (coords[i][0]+5,coords[i][1]-5), font, font_scale, color, thickness)
            else:
                cv2.putText(output_image, predicted_char, (coords[i][0]+5,coords[i][1]-5), font, font_scale, color, thickness)
                output_string += predicted_char

        
        output_image = Image.fromarray(output_image, 'RGB')
        data = io.BytesIO()
        output_image.save(data, "JPEG") 
        output_image = base64.b64encode(data.getvalue()).decode('utf-8')
        return jsonify({'output_image': output_image, 'output_string': output_string})
    return render_template('index.html')

 