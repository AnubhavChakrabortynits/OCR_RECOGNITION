import cv2
import numpy as np
char_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C',
       'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'P', 'Q',
       'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']


char_list_sub = ['A','9','G','Q','8','6']  

mappings = {i: char_list[i] for i in range(len(char_list))}

font = cv2.FONT_HERSHEY_TRIPLEX
font_scale = 0.5
color = (255, 255, 0) 
thickness = 1
 
def predict(model, sub_model, img,mappings):

    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    img = cv2.resize(img,(32,32))
    img = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
 
    img = cv2.filter2D(img, -1, kernel)
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    img = cv2.dilate(img,(3,3),iterations=1)
    img = img/255.
    img = img.astype('float32')

    predval = model.predict(np.expand_dims(img,axis=0))
    argval =np.argmax(predval,axis=-1)
    result = mappings[argval[0]]
    
    if result in char_list_sub:
        predval_new = sub_model.predict(np.expand_dims(img,axis=0))
        argval_new =np.argmax(predval_new,axis=-1)
        result_new = mappings[argval_new[0]] 

        if result == '6' and result_new == 'G':
            return result
        return result_new

    return result


def get_results(uploaded_image):
    original_image = uploaded_image
    image = cv2.cvtColor(original_image,cv2.COLOR_BGR2GRAY)
    x,y = image.shape
    maxH = min(1000,x)  
    maxW = min(1000,y)
    original_image = cv2.resize(original_image,(maxW,maxH))


    image = cv2.resize(image,(maxW,maxH))
 
    _, black_white_image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    if black_white_image[10,10] == 255 or black_white_image[10,len(image[0])-10] == 255 or black_white_image[len(black_white_image)-1,10] == 255 or black_white_image[len(image)-10,len(image[0])-10] == 255:
        black_white_image = 255 - black_white_image

    num_labels, _, stats, _ = cv2.connectedComponentsWithStats(black_white_image, connectivity=8)
    output_image = original_image.copy()

    sorted_indices = sorted(range(num_labels), key=lambda i: (stats[i, cv2.CC_STAT_TOP],stats[i, cv2.CC_STAT_LEFT]))

    grouped_indices = []
    current_group = [sorted_indices[0]]

    for i in range(1, num_labels):
        current_index = sorted_indices[i]
        prev_index = current_group[-1]
    
        if abs(stats[current_index, cv2.CC_STAT_TOP] - stats[prev_index, cv2.CC_STAT_TOP]) <= 20:
            current_group.append(current_index)
        else:
            current_group.sort(key=lambda idx: stats[idx, cv2.CC_STAT_LEFT])
            grouped_indices.extend(current_group)
        
            current_group = [current_index]

    current_group.sort(key=lambda idx: stats[idx, cv2.CC_STAT_LEFT])
    grouped_indices.extend(current_group)
    sorted_indices = grouped_indices


    detected_contours = []
    coords = []
    for i in sorted_indices:
        if i == 0:
            continue 
        x, y, w, h, area = stats[i]
        
        widthFlag = w > 2 and w < 500 and w < (maxW-50)
        heightFlag = h > 15  and h < 500 and h < (maxH-10) 
        areaFlag = area > 15 and area < 100000
        
        if widthFlag and heightFlag and areaFlag:
            samp = image[y:y+h,x:x+w]
            samp = cv2.resize(samp,(32,32))
            coords.append((x,y))
            detected_contour = output_image[y:y+h,x:x+w]
            bordered_contour = cv2.copyMakeBorder(detected_contour, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=[0, 0, 0])
            detected_contours.append(bordered_contour)
            cv2.rectangle(output_image, (x-2, y-2), (x + w+2, y + h+2), (0, 1, 0), 2)
    output_image = output_image*255
    return detected_contours,output_image,coords




