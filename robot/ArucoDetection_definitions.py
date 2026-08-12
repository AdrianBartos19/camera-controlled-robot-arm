
import cv2
import numpy as np
import time


        
def getMarkerCoordinates(markers,ids,point=0): 
    
    marker_array=[]
    
    for marker in markers:
        marker_array.append([int(marker[0][point][0]),int(marker[0][point][1])])
    

    return marker_array,ids

def getMarkerCenter_foam(marker):
    left_top,ids =getMarkerCoordinates(marker,1,point=0) 
    right_top,ids =getMarkerCoordinates(marker,1,point=1)     
    left_bot,ids =getMarkerCoordinates(marker,1,point=2) 
    right_bot,ids =getMarkerCoordinates(marker,1,point=3) 
    #print(left_top)
    if bool(left_top):
        center_X=(left_top[0][0]+right_top[0][0]+left_bot[0][0]+right_bot[0][0])*0.25
        center_Y=(left_top[0][1]+right_top[0][1]+left_bot[0][1]+right_bot[0][1])*0.25
        markerCenter=[[int(center_X),int(center_Y)]]
    else:
        markerCenter=[[0,0]]
    
    return markerCenter

        
def draw_corners(img,corners):
    for corner in corners:    
        cv2.circle(img,(corner[0],corner[1]),10,(0,255,0),thickness=-1)       

def draw_numbers(img,corners,ids):
    number=0
    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = 4
    for corner in corners:    
        cv2.putText(img,str(ids[number]),(corner[0]+10,corner[1]+10), font, 2,(0,0,0),thickness)
        number=number+1
        
def show_spec(img,corners):
    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = 1
    amountOfCorners=len(corners)
    spec_string=str(amountOfCorners)+" markers found."
    cv2.putText(img,spec_string,(15,15), font, 0.5,(0,0,250),thickness)
        
def draw_field(img,corners,ids):   
    if len(corners)==4:
        markers_sorted=[0,0,0,0]  
        for sorted_corner_id in [1,2,3,4]:
            index=ids.index(sorted_corner_id)
            markers_sorted[sorted_corner_id-1]=corners[index]
        contours = np.array(markers_sorted)      
        overlay = img.copy()
        cv2.fillPoly(overlay, pts =[contours], color=(255,215,0))
        alpha = 0.4  
        
        img_new=cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
        squarefound=True
    else:
        img_new=img
        squarefound=False
    return img_new,squarefound


def order_points(pts):
	
	rect = np.zeros((4, 2), dtype = "float32")
	
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
	
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
	
	return rect



def four_point_transform(image, pts):
	
	rect = order_points(pts)
	(tl, tr, br, bl) = rect
	
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))
	
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))

	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")
	
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
	# return the warped image
	return warped